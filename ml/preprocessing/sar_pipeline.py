import os
import shutil
import time
import logging
import subprocess
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class SARPreprocessor:
    """Wraps ESA SNAP's Graph Processing Tool (gpt) for Sentinel-1 preprocessing."""

    def __init__(self, raw_dir: Path, output_dir: Path, gpt_path: str = None):
        self.raw_dir = raw_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.gpt_path = gpt_path or self._find_gpt_executable()
        
        if not self.gpt_path or not os.path.exists(self.gpt_path):
            raise FileNotFoundError(
                "ESA SNAP gpt executable could not be found automatically. "
                "Please specify gpt_path explicitly when initializing SARPreprocessor."
            )
        logger.info(f"Using SNAP GPT executable at: {self.gpt_path}")

    def _find_gpt_executable(self) -> Optional[str]:
        system_gpt = shutil.which("gpt") or shutil.which("gpt.exe")
        if system_gpt:
            return system_gpt

        local_appdata = os.environ.get("LOCALAPPDATA", "")
        candidates = [
            r"C:\Program Files\snap\bin\gpt.exe",
            r"C:\Program Files\esa-snap\bin\gpt.exe",
            r"C:\Program Files\snap14\bin\gpt.exe",
            os.path.join(local_appdata, r"Programs\snap\bin\gpt.exe"),
            os.path.join(local_appdata, r"snap\bin\gpt.exe"),
        ]

        for path in candidates:
            if os.path.exists(path):
                return path
        return None

    def create_graph_xml(self, input_file: Path, output_file: Path) -> Path:
        wkt_polygon = "POLYGON ((9.75 46.75, 9.90 46.75, 9.90 46.88, 9.75 46.88, 9.75 46.75))"
        
        xml_content = f"""<graph id="S1_Preprocessing">
            <version>1.0</version>
            <node id="Read">
                <operator>Read</operator>
                <sources/>
                <parameters>
                    <file>{input_file.resolve()}</file>
                </parameters>
            </node>
            
            <node id="Apply-Orbit-File">
                <operator>Apply-Orbit-File</operator>
                <sources>
                    <sourceProduct refid="Read"/>
                </sources>
                <parameters>
                    <orbitType>Sentinel Precise (Auto Download)</orbitType>
                    <polyDegree>3</polyDegree>
                    <continueOnFail>true</continueOnFail>
                </parameters>
            </node>
            
            <node id="ThermalNoiseRemoval">
                <operator>ThermalNoiseRemoval</operator>
                <sources>
                    <sourceProduct refid="Apply-Orbit-File"/>
                </sources>
                <parameters>
                    <selectedPolarisations>VV,VH</selectedPolarisations>
                    <removeThermalNoise>true</removeThermalNoise>
                </parameters>
            </node>
            
            <node id="Calibration">
                <operator>Calibration</operator>
                <sources>
                    <sourceProduct refid="ThermalNoiseRemoval"/>
                </sources>
                <parameters>
                    <selectedPolarisations>VV,VH</selectedPolarisations>
                    <outputSigmaBand>true</outputSigmaBand>
                </parameters>
            </node>
            
            <node id="Speckle-Filter">
                <operator>Speckle-Filter</operator>
                <sources>
                    <sourceProduct refid="Calibration"/>
                </sources>
                <parameters>
                    <filter>Lee</filter>
                    <filterSizeX>3</filterSizeX>
                    <filterSizeY>3</filterSizeY>
                    <dampingFactor>2</dampingFactor>
                </parameters>
            </node>
            
            <node id="Terrain-Correction">
                <operator>Terrain-Correction</operator>
                <sources>
                    <sourceProduct refid="Speckle-Filter"/>
                </sources>
                <parameters>
                    <demName>Copernicus 30m Global DEM</demName>
                    <demResamplingMethod>BILINEAR_INTERPOLATION</demResamplingMethod>
                    <imgResamplingMethod>BILINEAR_INTERPOLATION</imgResamplingMethod>
                    <pixelSpacingInMeter>10.0</pixelSpacingInMeter>
                    <mapProjection>EPSG:32632</mapProjection>
                    <saveSelectedSourceBand>true</saveSelectedSourceBand>
                </parameters>
            </node>

            <node id="Subset">
                <operator>Subset</operator>
                <sources>
                    <sourceProduct refid="Terrain-Correction"/>
                </sources>
                <parameters>
                    <geoRegion>{wkt_polygon}</geoRegion>
                    <copyMetadata>true</copyMetadata>
                </parameters>
            </node>
            
            <node id="Write">
                <operator>Write</operator>
                <sources>
                    <sourceProduct refid="Subset"/>
                </sources>
                <parameters>
                    <file>{output_file.resolve()}</file>
                    <formatName>GeoTIFF-BigTIFF</formatName>
                </parameters>
            </node>
        </graph>"""

        xml_path = self.output_dir / f"temp_graph_{input_file.stem}.xml"
        with open(xml_path, "w") as f:
            f.write(xml_content)
            
        return xml_path

    def process_scene(self, zip_file: Path):
        logger.info(f"Preparing pipeline for {zip_file.name}...")
        
        out_name = zip_file.stem.replace("GRDH", "ARD") + ".tif"
        out_path = self.output_dir / out_name
        
        if out_path.exists():
            logger.info(f"Processed file already exists: {out_name}. Skipping.")
            return out_path

        xml_path = self.create_graph_xml(zip_file, out_path)
        
        logger.info(f"Executing SNAP gpt for {zip_file.name} (This may take 5-15 minutes per scene)...")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [self.gpt_path, str(xml_path.resolve()), "-e"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False
            )
            
            if not out_path.exists():
                logger.error(f"SNAP silent failure for {zip_file.name}. No output file created!\nSNAP Log:\n{result.stdout}")
                return None
                
            elapsed = (time.time() - start_time) / 60
            logger.info(f"Success! Processed {out_name} in {elapsed:.2f} minutes.")
            
        except Exception as e:
            logger.error(f"Execution error for {zip_file.name}: {e}")
        finally:
            if xml_path.exists():
                xml_path.unlink()

        return out_path

if __name__ == "__main__":
    raw_dir = Path("data/raw")
    output_dir = Path("data/interim/sar")
    
    try:
        processor = SARPreprocessor(raw_dir, output_dir)
        s1_zips = list(raw_dir.glob("S1*.zip"))
        
        if not s1_zips:
            logger.error(f"No Sentinel-1 ZIP files found in {raw_dir}")
        else:
            logger.info(f"Found {len(s1_zips)} scenes ready for terrain correction processing.")
            for zip_file in s1_zips:
                processor.process_scene(zip_file)
            logger.info("SAR processing complete! ARD generated.")
            
    except Exception as e:
        logger.error(f"Pipeline error: {e}")