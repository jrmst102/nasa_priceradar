import os
import datetime as dt
from .config import Config
from .pipeline import run_pipeline

def _parse_date(s): 
    return dt.datetime.strptime(s, "%Y-%m-%d").date()

def main(cfg_dict):
    cfg = Config(
        stores_csv=cfg_dict["stores_csv"],
        prices_csv=cfg_dict["prices_csv"],
        event_start=_parse_date(cfg_dict["event_start"]),
        event_end=_parse_date(cfg_dict["event_end"]),
        imerg_path=cfg_dict["imerg_path"],
        baseline_days=cfg_dict.get("baseline_days", 28),
        precipitation_threshold_mm_24h=cfg_dict.get("precipitation_threshold_mm_24h", 50.0),
        outdir=cfg_dict.get("outdir", "out"),
        alpha_zmad=cfg_dict.get("alpha_zmad", 4.0),
        beta_pct=cfg_dict.get("beta_pct", 0.25),
        crs_epsg=cfg_dict.get("crs_epsg", 4326)
    )
    flags_csv, map_html = run_pipeline(cfg)
    print(f"[OK] Wrote: {flags_csv}")
    print(f"[OK] Wrote: {map_html}")
