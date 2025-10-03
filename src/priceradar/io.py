import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def ensure_outdir(path: str):
    os.makedirs(path, exist_ok=True)

def _find_col(df, candidates):
    cols = {c.lower(): c for c in df.columns}
    for k in candidates:
        if k in cols:
            return cols[k]
    return None

def load_stores(path: str, crs_epsg: int) -> gpd.GeoDataFrame:
    df = pd.read_csv(path)
    lat = _find_col(df, ["latitude","lat","store_lat","y"])
    lon = _find_col(df, ["longitude","lon","lng","store_lon","x"])
    sid = _find_col(df, ["store_id","storeid","id"])
    sname = _find_col(df, ["store_name","name","storename","label","title"])
    if not (lat and lon and sid):
        raise ValueError("Stores CSV must include store_id, latitude, longitude (flexible names accepted).")
    if not sname:
        sname = sid
    gdf = gpd.GeoDataFrame(
        df.rename(columns={lat:"latitude", lon:"longitude", sid:"store_id", sname:"store_name"})[["store_id","store_name","latitude","longitude"]].copy(),
        geometry=[Point(xy) for xy in zip(df[lon], df[lat])],
        crs=f"EPSG:{crs_epsg}"
    )
    return gdf

def load_prices(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    date = _find_col(df, ["date","day","pricedate"])
    sid = _find_col(df, ["store_id","storeid","sid"])
    sku = _find_col(df, ["sku_id","product_id","skuid","pid"])
    price = _find_col(df, ["price","unit_price","sale_price"])
    if not (date and sid and sku and price):
        raise ValueError("Prices CSV must include date, store_id, sku_id, price (flexible names accepted).")
    df = df.rename(columns={date:"date", sid:"store_id", sku:"sku_id", price:"price"})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df = df.dropna(subset=["date","store_id","sku_id","price"])
    return df
