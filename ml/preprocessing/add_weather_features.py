import logging
import rasterio
import xarray as xr
import rioxarray
import numpy as np
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def integrate_era5(master_tif_path: Path, era5_nc_path: Path, output_tif_path: Path):
    if not era5_nc_path.exists():
        logger.error(f"ERA5 file not found at {era5_nc_path}.")
        return

    logger.info(f"Loading master SAR grid from {master_tif_path.name}")
    master = rioxarray.open_rasterio(master_tif_path)
    
    logger.info(f"Loading ERA5 data from {era5_nc_path.name}")
    
    ds = None
    for engine in [None, "h5netcdf", "netcdf4", "cfgrib"]:
        try:
            if engine:
                ds = xr.open_dataset(era5_nc_path, engine=engine)
            else:
                ds = xr.open_dataset(era5_nc_path)
            logger.info(f"Successfully opened file using engine: {engine or 'auto'}")
            break
        except Exception:
            continue

    if ds is None:
        raise ValueError(
            f"Could not open {era5_nc_path}. Ensure the file is a valid NetCDF/GRIB "
            "file and not an empty (0 KB) corrupted download or HTML error response."
        )

    if 'time' in ds.dims:
        ds_time = ds.isel(time=0) 
    else:
        ds_time = ds
        
    ds_time = ds_time.rio.write_crs("EPSG:4326")
    
    new_bands = []
    variables = ['tp', 't2m', 'sd'] 
    
    for var in variables:
        if var not in ds_time.data_vars:
            logger.warning(f"Variable '{var}' not found in dataset. Filling with zeros.")
            new_bands.append(np.zeros((master.shape[1], master.shape[2]), dtype=np.float32))
            continue
            
        logger.info(f"Resampling '{var}' to 10m master grid via bilinear interpolation...")
        da = ds_time[var]
        da_resampled = da.rio.reproject_match(master, resampling=rasterio.enums.Resampling.bilinear)
        da_filled = da_resampled.fillna(0)
        
        # Squeeze out any accidental 1D dimensions rioxarray might add to ensure it's strictly 2D (H, W)
        new_bands.append(np.squeeze(da_filled.values))
        
    logger.info("Stacking atmospheric variables into 3D array...")
    # Stack creates a 3D array of shape (3, H, W)
    weather_array = np.stack(new_bands, axis=0) 
    
    with rasterio.open(master_tif_path) as src:
        meta = src.meta.copy()
        sar_dem_array = src.read() # Shape: (7, H, W)
        
    # Concatenate the 7-band and 3-band arrays along the depth/band axis
    final_stack = np.concatenate((sar_dem_array, weather_array), axis=0) 
    meta.update(count=final_stack.shape[0])
    
    logger.info(f"Writing {final_stack.shape[0]}-band tensor to {output_tif_path}")
    with rasterio.open(output_tif_path, 'w', **meta) as dst:
        dst.write(final_stack)
        
    logger.info("ERA5 integration complete.")

if __name__ == "__main__":
    master_tif = Path("data/processed/ml_feature_stack.tif")
    era5_nc = Path("data/raw/era5_weather.nc") 
    out_tif = Path("data/processed/ml_feature_stack_10band.tif")
    
    integrate_era5(master_tif, era5_nc, out_tif)