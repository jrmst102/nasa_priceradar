# NASA PriceRadar 🚨🌧️
**Prototype 1: Storm → Price Anomaly Radar**

Detect potential price-gouging signals around storms by combining **retail prices** with **NASA IMERG precipitation**.

---

## Repo Layout
```
nasa_priceradar/
├─ README.md
├─ requirements.txt
├─ environment.yml
├─ setup.cfg
├─ .gitignore
├─ Dockerfile
├─ Makefile
├─ configs/
│  └─ example_nyc.yml
├─ scripts/
│  └─ run_priceradar.py
├─ src/priceradar/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ io.py
│  ├─ baseline.py
│  ├─ anomalies.py
│  ├─ exposure.py
│  ├─ mapviz.py
│  ├─ pipeline.py
│  └─ cli.py
├─ tests/
│  └─ test_baseline.py
└─ .github/workflows/
   └─ ci.yml
```

## Using Mancino data (keep data in a separate repo)
You have two clean options:

### Option A — Git submodule (recommended)
```bash
git submodule add https://github.com/jrmst102/mancino external/mancino
git commit -m "Add Mancino as submodule"
```
Then point your config to CSVs inside `external/mancino/...`.

### Option B — Local clone + ENV var
Clone Mancino anywhere and set `MANCINO_PATH`:
```bash
export MANCINO_PATH=/path/to/mancino
```
The example config uses `${MANCINO_PATH}` placeholders.

---

## Quick Start
1) Install deps (Python 3.10+ recommended):
```bash
pip install -r requirements.txt
```

2) Prepare a **24h IMERG accumulation** raster for your event window (GeoTIFF or NetCDF). For a fast demo, clip to NYC.
   - Put it somewhere like `data/imerg_24h_accum.tif`.

3) Edit `configs/example_nyc.yml` to set your paths and dates.

4) Run:
```bash
python scripts/run_priceradar.py --config configs/example_nyc.yml
```

Outputs:
- `out/baseline_stats.csv` — per (store, sku) baseline median & MAD
- `out/flags.csv` — anomaly + exposure table with %Δ, z(MAD), precip mm
- `out/map_flags.html` — interactive map with flagged stores/SKUs

---

## Configuration (YAML)
```yaml
# configs/example_nyc.yml
stores_csv: "${MANCINO_PATH}/data/stores/stores.csv"
prices_csv: "${MANCINO_PATH}/data/prices/daily_prices.csv"
event_start: "2025-09-27"
event_end: "2025-10-02"
imerg_path: "data/imerg_24h_accum.tif"
baseline_days: 28
precipitation_threshold_mm_24h: 50.0
outdir: "out"
alpha_zmad: 4.0       # anomaly sensitivity (z(MAD) threshold)
beta_pct: 0.25        # anomaly sensitivity (percent change)
crs_epsg: 4326
```

> If you don’t have daily price tables, aggregate your transactions to **daily median price per (store, sku)** first.

---

## Dev Notes
- **Robust stats:** We use MAD-based z-scores for resilience to outliers.
- **Exposure gating:** A price jump only flags if the store was **storm-exposed** (precip ≥ threshold).
- **Map:** Folium generates a lightweight HTML you can share.
- **Extensible:** Add inventory/logistics context to reduce false positives.

---

## Docker (optional)
```bash
docker build -t nasa_priceradar .
docker run --rm -it -v $PWD:/app -e MANCINO_PATH=$MANCINO_PATH nasa_priceradar   python scripts/run_priceradar.py --config configs/example_nyc.yml
```

## CI (optional)
GitHub Actions runs lint + unit tests on push/PR.

---

## License
MIT
