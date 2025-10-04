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

def _coerce_key_types(left: pd.DataFrame, right: pd.DataFrame, key: str = "store_id"):
    if key in left.columns and key in right.columns and left[key].dtype != right[key].dtype:
        return left.assign(**{key: left[key].astype(str)}), right.assign(**{key: right[key].astype(str)})
    return left, right

def run_pipeline(cfg: Config):
    ensure_outdir(cfg.outdir)

    # Load inputs
    stores = load_stores(cfg.stores_csv, cfg.crs_epsg)
    prices = load_prices(cfg.prices_csv)

    # Baseline + anomalies
    baseline = build_baseline(prices, cfg.event_start, cfg.baseline_days)
    baseline.to_csv(os.path.join(cfg.outdir, "baseline_stats.csv"), index=False)
    anomalies = compute_event_anomalies(
        prices, cfg.event_start, cfg.event_end, baseline,
        alpha=cfg.alpha_zmad, beta_pct=cfg.beta_pct
    )

    # Exposure from IMERG
    da = load_imerg(cfg.imerg_path)
    stores["precip_mm_24h"] = sample_precip_at_points(da, stores)

    # Merge exposure
    exposure = stores[["store_id", "precip_mm_24h"]].copy()
    anomalies, exposure = _coerce_key_types(anomalies, exposure, "store_id")
    anomalies = anomalies.merge(exposure, on="store_id", how="left")

    # Normalize precip column (if suffixed or missing)
    if "precip_mm_24h" not in anomalies.columns:
        pcols = [c for c in anomalies.columns if c.startswith("precip_mm_24h")]
        if pcols:
            anomalies["precip_mm_24h"] = anomalies[pcols[0]]
        else:
            anomalies["precip_mm_24h"] = 0.0  # last resort

    # Exposure gate
    anomalies["exposed"] = anomalies["precip_mm_24h"] >= cfg.precipitation_threshold_mm_24h

    # Bring identity/coords only
    store_cols = [c for c in ["store_id", "store_name", "latitude", "longitude"] if c in stores.columns]
    stores_id = stores[store_cols].copy()
    anomalies, stores_id = _coerce_key_types(anomalies, stores_id, "store_id")
    out = anomalies.merge(stores_id, on="store_id", how="left")

    # Final flag
    out["flagged"] = out["anomaly_rule"] & out["exposed"]

    # Debug outputs
    anomalies.to_csv(os.path.join(cfg.outdir, "_debug_anomalies.csv"), index=False)
    stores.to_csv(os.path.join(cfg.outdir, "_debug_stores.csv"), index=False)

    # Safe column selection
    desired = [
        "store_id","store_name","latitude","longitude",
        "sku_id","price","baseline_median","delta","pct_change","zscore_mad",
        "precip_mm_24h","exposed","flagged"
    ]
    keep = [c for c in desired if c in out.columns]
    if "precip_mm_24h" not in keep:  # guarantee it's present
        out["precip_mm_24h"] = anomalies["precip_mm_24h"]
        keep = [c for c in desired if c in out.columns]
    out = out[keep].sort_values(["flagged","pct_change"], ascending=[False, False])

    # Write outputs
    flags_csv = os.path.join(cfg.outdir, "flags.csv")
    out.to_csv(flags_csv, index=False)

    map_path = os.path.join(cfg.outdir, "map_flags.html")
    make_map(out, map_path, stores[["store_id","store_name","latitude","longitude"]])

    return flags_csv, map_path
