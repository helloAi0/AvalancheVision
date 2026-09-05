import logging
import rasterio
import numpy as np
import requests
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from pathlib import Path
from pystac_client import Client
import planetary_computer as pc

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DEMProcessor:
    """Fetches and processes Copernicus DEM data for terrain feature extraction."""

    def __init__(self, bbox: list, output_dir: Path):
        self.bbox = bbox
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Planetary Computer STAC endpoint (No authentication required for DEMs)
        self.stac_endpoint = "https://planetarycomputer.microsoft.com/api/stac/v1"
        
        # UTM Zone 32N (EPSG:32632) is optimal for the Swiss Alps (Davos)
        self.target_crs = "EPSG:32632" 

    def fetch_dem_tiles(self) -> list:
        """Queries and downloads required Copernicus DEM GLO-30 tiles."""
        logger.info(f"Querying Planetary Computer STAC for DEM tiles over {self.bbox}...")
        client = Client.open(self.stac_endpoint, modifier=pc.sign_inplace)
        
        search = client.search(
            collections=["cop-dem-glo-30"],
            bbox=self.bbox,
        )
        
        items = list(search.items())
        logger.info(f"Found {len(items)} DEM tile(s) intersecting the bounding box.")
        
        tile_paths = []
        for item in items:
            url = item.assets["data"].href
            tile_id = item.id
            out_path = self.output_dir / f"{tile_id}.tif"
            tile_paths.append(out_path)
            
            if out_path.exists():
                logger.info(f"Tile {tile_id} already exists. Skipping download.")
                continue
                
            logger.info(f"Downloading DEM tile: {tile_id}...")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(out_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        
        return tile_paths

    def mosaic_and_clip(self, tile_paths: list) -> Path:
        """Merges multiple DEM tiles and clips them to the exact bounding box."""
        logger.info("Mosaicking DEM tiles and clipping to bounding box...")
        src_files = [rasterio.open(fp) for fp in tile_paths]
        
        mosaic, out_trans = merge(src_files, bounds=self.bbox)
        out_meta = src_files[0].meta.copy()
        
        out_meta.update({
            "driver": "GTiff",
            "height": mosaic.shape[1],
            "width": mosaic.shape[2],
            "transform": out_trans
        })
        
        for src in src_files:
            src.close()
            
        raw_mosaic_path = self.output_dir / "davos_dem_epsg4326.tif"
        with rasterio.open(raw_mosaic_path, "w", **out_meta) as dest:
            dest.write(mosaic)
            
        return raw_mosaic_path

    def reproject_to_utm(self, raw_mosaic_path: Path) -> Path:
        """Reprojects the DEM to a metric CRS for accurate mathematical gradients."""
        logger.info(f"Reprojecting DEM to {self.target_crs} (Metric)...")
        reprojected_path = self.output_dir / "davos_dem_utm.tif"
        
        with rasterio.open(raw_mosaic_path) as src:
            transform, width, height = calculate_default_transform(
                src.crs, self.target_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': self.target_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(reprojected_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=self.target_crs,
                        resampling=Resampling.bilinear)
        
        return reprojected_path

    def extract_terrain_features(self, dem_path: Path):
        """Calculates Slope and Aspect arrays using numpy gradients."""
        logger.info("Calculating Slope and Aspect features...")
        with rasterio.open(dem_path) as src:
            elevation = src.read(1)
            transform = src.transform
            meta = src.meta.copy()
            
        # Pixel resolutions in meters (dx and dy)
        dx = transform.a
        dy = abs(transform.e) 
        
        # Calculate gradients (py maps to rows/Y-axis, px maps to cols/X-axis)
        py, px = np.gradient(elevation, dy, dx)
        
        # Slope calculation
        slope = np.degrees(np.arctan(np.sqrt(px**2 + py**2)))
        
        # Aspect calculation (0=North, 90=East, 180=South, 270=West)
        aspect = np.degrees(np.arctan2(-px, py))
        aspect = np.where(aspect < 0, 360 + aspect, aspect)
        
        # Flat surfaces (< 0.01 degree slope) have no definable aspect
        aspect = np.where(slope < 0.01, -1, aspect)

        slope_path = self.output_dir / "davos_slope.tif"
        aspect_path = self.output_dir / "davos_aspect.tif"

        # Update metadata for float outputs
        meta.update(dtype=rasterio.float32, nodata=-1)
        
        with rasterio.open(slope_path, 'w', **meta) as dst:
            dst.write(slope.astype(rasterio.float32), 1)
            
        with rasterio.open(aspect_path, 'w', **meta) as dst:
            dst.write(aspect.astype(rasterio.float32), 1)
            
        logger.info(f"Successfully saved dem, slope, and aspect layers to {self.output_dir}")


if __name__ == "__main__":
    davos_bbox = [9.75, 46.75, 9.90, 46.88]
    output_dir = Path("data/interim/terrain")
    
    processor = DEMProcessor(davos_bbox, output_dir)
    
    # 1. Fetch from Planetary Computer
    tiles = processor.fetch_dem_tiles()
    
    # 2. Mosaic and crop to exactly fit our bounding box
    raw_dem = processor.mosaic_and_clip(tiles)
    
    # 3. Reproject to UTM Zone 32N so slope calculations use meters, not degrees
    utm_dem = processor.reproject_to_utm(raw_dem)
    
    # 4. Generate Slope and Aspect TIFFs
    processor.extract_terrain_features(utm_dem)
    logger.info("Terrain pipeline complete.")