import xarray as xr
import numpy as np
import pandas as pd
from pathlib import Path

def create_synthetic_era5():
    out_path = Path("data/raw/era5_weather.nc")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Coordinates covering the SAR bounding box (Swiss Alps / Davos)
    lats = np.linspace(46.9, 46.7, 10)
    lons = np.linspace(9.7, 10.0, 10)
    times = pd.date_range("2024-01-10", periods=1)

    # Synthetic physical data: Precipitation, 2m Temp (Kelvin), Snow Depth (m)
    tp = np.random.uniform(0, 0.02, size=(1, 10, 10)).astype(np.float32)
    t2m = np.random.uniform(265, 273, size=(1, 10, 10)).astype(np.float32) 
    sd = np.random.uniform(0.5, 2.5, size=(1, 10, 10)).astype(np.float32) 

    ds = xr.Dataset(
        data_vars={
            "tp": (["time", "latitude", "longitude"], tp),
            "t2m": (["time", "latitude", "longitude"], t2m),
            "sd": (["time", "latitude", "longitude"], sd),
        },
        coords={
            "time": times,
            "latitude": lats,
            "longitude": lons,
        }
    )

    ds.to_netcdf(out_path, engine="netcdf4")
    print(f"Synthetic ERA5 NetCDF created successfully at {out_path}")

if __name__ == "__main__":
    create_synthetic_era5()