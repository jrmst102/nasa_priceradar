import datetime as dt
import numpy as np
import pandas as pd

def compute_event_anomalies(prices: pd.DataFrame, event_start: dt.date, event_end: dt.date, baseline: pd.DataFrame,
                            alpha: float = 4.0, beta_pct: float = 0.25) -> pd.DataFrame:
    ev = prices[(prices["date"] >= event_start) & (prices["date"] <= event_end)].copy()
    if ev.empty:
        raise ValueError("No price data in event window. Check dates.")
    latest = ev.sort_values("date").groupby(["store_id","sku_id"]).tail(1)
    df = latest.merge(baseline, on=["store_id","sku_id"], how="left")
    df["delta"] = df["price"] - df["baseline_median"]
    df["zscore_mad"] = df["delta"] / (1.4826 * df["baseline_mad"])
    df["pct_change"] = (df["price"] / df["baseline_median"] - 1.0).replace([np.inf,-np.inf], float("nan"))
    df["anomaly_rule"] = (df["zscore_mad"].abs() >= alpha) | (df["pct_change"].abs() >= beta_pct)
    return df
