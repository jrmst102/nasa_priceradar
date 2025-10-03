from typing import Optional
import numpy as np
import geopandas as gpd
import rioxarray as rxr
import xarray as xr

def load_imerg(imerg_path: str):
    if imerg_path.lower().endswith((".tif",".tiff")):
        da = rxr.open_rasterio(imerg_path).squeeze()
        if "y" in da.coords and "x" in da.coords:
            da = da.rename({"y":"lat","x":"lon"})
        return da
    elif imerg_path.lower().endswith((".nc",".nc4")):
        ds = xr.open_dataset(imerg_path)
        for var in ["precipitationCal","precipitation","HQprecipitation"]:
            if var in ds.data_vars:
                da = ds[var]
                if "latitude" in ds.coords: da = da.rename({"latitude":"lat"})
                if "longitude" in ds.coords: da = da.rename({"longitude":"lon"})
                if "latitude" in da.coords: da = da.rename({"latitude":"lat"})
                if "longitude" in da.coords: da = da.rename({"longitude":"lon"})
                return da
        raise ValueError("Could not find a precipitation variable in NetCDF; edit load_imerg() to match your file.")
    else:
        raise ValueError("Unsupported IMERG file format (.tif/.tiff or .nc/.nc4 only).")

def sample_precip_at_points(da, gdf_points: gpd.GeoDataFrame):
    lats = da["lat"].values
    lons = da["lon"].values
    def nearest_idx(val, arr):
        return int(np.abs(arr - val).argmin())
    vals = []
    for _, row in gdf_points.iterrows():
        lat, lon = row["latitude"], row["longitude"]
        i = nearest_idx(lat, lats)
        j = nearest_idx(lon, lons)
        try:
            v = float(da.values[i, j])
        except Exception:
            v = float("nan")
        vals.append(v)
    return vals
