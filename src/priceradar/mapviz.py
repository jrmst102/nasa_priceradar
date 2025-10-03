import folium
import pandas as pd

def make_map(df: pd.DataFrame, out_html: str, stores_df: pd.DataFrame):
    flagged = df[df["flagged"]==True].copy()
    if flagged.empty:
        flagged = df[df["anomaly_rule"]==True].copy()
    if not flagged.empty:
        center_lat = flagged["latitude"].mean()
        center_lon = flagged["longitude"].mean()
    else:
        center_lat = stores_df["latitude"].mean()
        center_lon = stores_df["longitude"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="OpenStreetMap")
    def popup_text(r):
        return (f"<b>{r.get('store_name')}</b><br>"
                f"SKU: {r.get('sku_id')}<br>"
                f"Price: {r.get('price'):.2f} (baseline {r.get('baseline_median'):.2f})<br>"
                f"%Δ: {100*r.get('pct_change',0):.1f} | z(MAD): {r.get('zscore_mad',0):.2f}<br>"
                f"Precip 24h: {r.get('precip_mm_24h',0):.1f} mm | Exposed: {bool(r.get('exposed'))}<br>"
                f"Flagged: {bool(r.get('flagged'))}")
    for _, r in flagged.iterrows():
        folium.CircleMarker(
            location=[r["latitude"], r["longitude"]],
            radius=6,
            fill=True,
            weight=1,
            popup=folium.Popup(popup_text(r), max_width=300),
        ).add_to(m)
    m.save(out_html)
