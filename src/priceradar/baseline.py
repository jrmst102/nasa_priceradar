import datetime as dt
import numpy as np
import pandas as pd

def _mad(arr):
    med = np.median(arr)
    return np.median(np.abs(arr - med))

def build_baseline(prices: pd.DataFrame, event_start: dt.date, baseline_days: int) -> pd.DataFrame:
    start = event_start - dt.timedelta(days=baseline_days)
    pre = prices[(prices["date"] >= start) & (prices["date"] < event_start)].copy()
    if pre.empty:
        raise ValueError("No price data in baseline window. Check dates or baseline_days.")
    grp = pre.groupby(["store_id","sku_id"])["price"]
    baseline = grp.agg(baseline_median=("median"), baseline_mad=(lambda x: _mad(x.values)))
    baseline = baseline.reset_index()
    baseline["baseline_mad"] = baseline["baseline_mad"].replace(0, 0.01)
    return baseline
