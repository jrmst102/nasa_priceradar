from dataclasses import dataclass
import datetime as dt
from typing import Optional

@dataclass
class Config:
    stores_csv: str
    prices_csv: str
    event_start: dt.date
    event_end: dt.date
    imerg_path: str
    baseline_days: int = 28
    precipitation_threshold_mm_24h: float = 50.0
    outdir: str = "out"
    alpha_zmad: float = 4.0
    beta_pct: float = 0.25
    crs_epsg: int = 4326
