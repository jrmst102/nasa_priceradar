import datetime as dt
import pandas as pd
from priceradar.baseline import build_baseline

def test_build_baseline_basic():
    data = [
        {"date":"2025-09-05","store_id":1,"sku_id":"A","price":10.0},
        {"date":"2025-09-10","store_id":1,"sku_id":"A","price":10.0},
        {"date":"2025-09-20","store_id":1,"sku_id":"A","price":10.0},
        {"date":"2025-09-22","store_id":1,"sku_id":"B","price":5.0},
        {"date":"2025-09-26","store_id":1,"sku_id":"B","price":5.2},
    ]
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    event_start = dt.date(2025,9,27)
    baseline = build_baseline(df, event_start, 28)
    assert {"store_id","sku_id","baseline_median","baseline_mad"} <= set(baseline.columns)
    assert len(baseline) == 2
