import os
from dotenv import load_dotenv 
import time
import logging
import requests
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from tqdm import tqdm

from backend.core.config import settings

load_dotenv()  

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Sentinel1IngestEngine:
    """Ingestion engine for Sentinel-1 SAR imagery via Copernicus Data Space Ecosystem."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or settings.CDSE_CLIENT_ID
        self.client_secret = client_secret or settings.CDSE_CLIENT_SECRET
        self.stac_url = settings.CDSE_STAC_URL
        self.odata_url = settings.CDSE_ODATA_URL
        self.token_url = settings.CDSE_TOKEN_URL
        self._access_token: Optional[str] = None

    def authenticate(self) -> bool:
        """Obtains OAuth2 bearer token from CDSE auth realm using direct portal user accounts."""
        # Pull values directly from your raw .env file 
        username = os.getenv("CDSE_USERNAME")
        password = os.getenv("CDSE_PASSWORD")

        if not username or not password or "your_registered" in username:
            logger.warning("CDSE master profile credentials missing or invalid in .env file.")
            return False

        # Official Keycloak payload format for master data stream allocation
        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": "cdse-public",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            response = requests.post(self.token_url, data=payload, headers=headers, timeout=30)
            response.raise_for_status()
            self._access_token = response.json().get("access_token")
            logger.info("Successfully authenticated master token profile with Copernicus Ecosystem.")
            return True
        except requests.RequestException as e:
            logger.error(f"Authentication profile generation failed: {e}")
            return False



    def search_scenes_stac(
        self,
        bbox: List[float],
        start_date: str,
        end_date: str,
        max_items: int = 20
    ) -> List[Dict[str, Any]]:
        """Searches Sentinel-1 scenes using Copernicus STAC Catalog API."""
        endpoint = f"{self.stac_url}/search"
        datetime_range = f"{start_date}T00:00:00Z/{end_date}T23:59:59Z"

        payload = {
            "collections": ["sentinel-1-grd"],
            "bbox": bbox,
            "datetime": datetime_range,
            "limit": max_items,
            "query": {
                "sar:instrument_mode": {"eq": "IW"}
            }
        }

        headers = {"Content-Type": "application/json"}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=20)
            if response.status_code == 200:
                features = response.json().get("features", [])
                logger.info(f"STAC Search returned {len(features)} Sentinel-1 scenes.")
                return features
            else:
                logger.warning(f"STAC search failed (Status {response.status_code}): {response.text}")
        except requests.RequestException as e:
            logger.warning(f"STAC search attempt error: {e}")

        return []

    def extract_scene_metadata(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """Parses scene entry into structured dictionary, cleaning scene_name."""
        properties = feature.get("properties", {})
        
        raw_id = feature.get("id", "UNKNOWN")
        raw_title = properties.get("title") or raw_id

        # Clean title by stripping _COG suffix
        scene_name = raw_title.replace("_COG", "").replace(".SAFE", "")

        # Extract UUID if directly present in feature properties
        uuid = properties.get("id") or feature.get("uuid")

        return {
            "uuid": uuid,
            "scene_name": scene_name,
            "datetime": properties.get("datetime"),
            "orbit_direction": str(properties.get("sat:orbit_state", "UNKNOWN")).upper(),
            "relative_orbit": properties.get("sat:relative_orbit", None),
            "raw_feature": feature
        }

    def resolve_product_uuid(self, scene_name: str) -> Optional[str]:
        """Queries CDSE OData using base product name to resolve exact UUID."""
        base_name = scene_name.replace("_COG", "").replace(".SAFE", "")
        logger.info(f"Resolving product UUID for {base_name}...")
        
        params = {
            "$filter": f"startswith(Name, '{base_name}')",
            "$select": "Id,Name"
        }
        headers = {}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        try:
            res = requests.get(self.odata_url, params=params, headers=headers, timeout=60)
            res.raise_for_status()
            value = res.json().get("value", [])
            if value:
                uuid = value[0].get("Id")
                matched_name = value[0].get("Name")
                logger.info(f"Resolved {matched_name} -> UUID: {uuid}")
                return uuid
        except Exception as e:
            logger.error(f"Failed to resolve UUID for {scene_name}: {e}")
        return None

    def select_co_registered_pair(
        self,
        features: List[Dict[str, Any]],
        event_date: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Selects optimal T1 (pre-event) and T2 (post-event) scenes matching relative orbit and pass."""
        event_dt = datetime.strptime(event_date, "%Y-%m-%d")
        
        parsed_scenes = []
        for feat in features:
            meta = self.extract_scene_metadata(feat)
            if meta["datetime"]:
                dt_str = meta["datetime"].split(".")[0].replace("Z", "")
                dt = datetime.fromisoformat(dt_str)
                parsed_scenes.append({"feature": feat, "metadata": meta, "dt": dt})

        pre_candidates = sorted([s for s in parsed_scenes if s["dt"] < event_dt], key=lambda s: abs((event_dt - s["dt"]).total_seconds()))
        post_candidates = sorted([s for s in parsed_scenes if s["dt"] >= event_dt], key=lambda s: abs((s["dt"] - event_dt).total_seconds()))

        for post in post_candidates:
            for pre in pre_candidates:
                if (post["metadata"]["orbit_direction"] == pre["metadata"]["orbit_direction"]):
                    logger.info(
                        f"Selected Pair -> T1 Pre-Event: {pre['metadata']['scene_name']} ({pre['metadata']['datetime']}) "
                        f"| T2 Post-Event: {post['metadata']['scene_name']} ({post['metadata']['datetime']}) "
                        f"| Orbit Pass: {post['metadata']['orbit_direction']}"
                    )
                    return pre["feature"], post["feature"]

        logger.warning("No matching pre/post SAR pair found in retrieved results.")
        return None, None

    def download_scene(self, uuid: str, scene_name: str, output_dir: Path) -> Optional[Path]:
        """Downloads Sentinel-1 product zip letting requests manage internal redirects natively."""
        output_file = Path(output_dir) / f"{scene_name}.zip"
        if output_file.exists():
            logger.info(f"Scene {scene_name} already exists at {output_file}")
            return output_file

        url = f"https://download.dataspace.copernicus.eu/odata/v1/Products({uuid})/$value"
        logger.info(f"Downloading {scene_name} (~1.6 GB)...")

        headers = {"Authorization": f"Bearer {self._access_token}"} if self._access_token else {}

        try:
            # allow_redirects=True allows native token handoff across the cluster storage nodes
            response = requests.get(url, headers=headers, stream=True, allow_redirects=True, timeout=60)
            response.raise_for_status()
            total_size = int(response.headers.get("content-length", 0))

            with open(output_file, "wb") as f, tqdm(
                desc=scene_name[:20] + "...",
                total=total_size,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(chunk_size=16384): # Doubled chunk size for faster downloads
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

            logger.info(f"Successfully downloaded {scene_name}")
            return output_file
        except Exception as e:
            logger.error(f"Download failed for {scene_name}: {e}")
            if output_file.exists():
                output_file.unlink()
            return None



if __name__ == "__main__":
    davos_bbox = [9.75, 46.75, 9.90, 46.88]
    engine = Sentinel1IngestEngine()
    
    if engine.authenticate():
        scenes = engine.search_scenes_stac(
            bbox=davos_bbox,
            start_date="2024-01-01",
            end_date="2024-01-20",
            max_items=10
        )
        if scenes:
            pre_scene, post_scene = engine.select_co_registered_pair(scenes, event_date="2024-01-10")
            
            if pre_scene and post_scene:
                pre_meta = engine.extract_scene_metadata(pre_scene)
                post_meta = engine.extract_scene_metadata(post_scene)

                pre_uuid = pre_meta["uuid"] or engine.resolve_product_uuid(pre_meta["scene_name"])
                post_uuid = post_meta["uuid"] or engine.resolve_product_uuid(post_meta["scene_name"])

                if pre_uuid and post_uuid:
                    logger.info("Starting downloads into data/raw...")
                    engine.download_scene(pre_uuid, pre_meta["scene_name"], settings.DATA_RAW_DIR)
                    engine.download_scene(post_uuid, post_meta["scene_name"], settings.DATA_RAW_DIR)
                else:
                    logger.error("Could not resolve product UUIDs required for download.")