import os
import datetime as dt
import pandas as pd
from .config import Config
from .io import ensure_outdir, load_stores, load_prices
from .baseline import build_baseline
from .anomalies import compute_event_anomalies
from .exposure import load_imerg, sample_precip_at_points
from .mapviz import make_map

def parse_date(s: str) -> dt.date:
    return dt.datetime.strptime(s, "%Y-%m-%d").date()

def run_pipeline(cfg: Config):
    ensure_outdir(cfg.outdir)
    stores = load_stores(cfg.stores_csv, cfg.crs_epsg)
    prices = load_prices(cfg.prices_csv)
    baseline = build_baseline(prices, cfg.event_start, cfg.baseline_days)
    baseline.to_csv(os.path.join(cfg.outdir, "baseline_stats.csv"), index=False)
    anomalies = compute_event_anomalies(prices, cfg.event_start, cfg.event_end, baseline,
                                        alpha=cfg.alpha_zmad, beta_pct=cfg.beta_pct)
    da = load_imerg(cfg.imerg_path)
    stores["precip_mm_24h"] = sample_precip_at_points(da, stores)
    exposure = stores[["store_id","precip_mm_24h"]].copy()
    anomalies = anomalies.merge(exposure, on="store_id", how="left")
    anomalies["exposed"] = anomalies["precip_mm_24h"] >= cfg.precipitation_threshold_mm_24h
    out = anomalies.merge(stores.drop(columns=["geometry"]), on="store_id", how="left")
    out["flagged"] = out["anomaly_rule"] & out["exposed"]
    out = out[["store_id","store_name","latitude","longitude","sku_id","price","baseline_median","delta",
               "pct_change","zscore_mad","precip_mm_24h","exposed","flagged"]].sort_values(
               ["flagged","pct_change"], ascending=[False, False])
    flags_csv = os.path.join(cfg.outdir, "flags.csv")
    out.to_csv(flags_csv, index=False)
    map_path = os.path.join(cfg.outdir, "map_flags.html")
    make_map(out, map_path, stores.drop(columns=["geometry"]))
    return flags_csv, map_path
