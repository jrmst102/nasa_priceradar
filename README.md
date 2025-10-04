# NASA PriceRadar
**Prototype 1: Storm - Price Anomaly Radar**

NASA Space Apps Challenge
School of Professional Studies
New York University
October 3rd, 2025
Prof. Jose Mendoza

Detect potential **price-gouging signals** around storms by combining **retail prices** with **NASA IMERG precipitation**.  
This repository contains the code only. Your **Mancino** repository holds the data.

---

## What’s included (current working version)
- Modular pipeline under `src/priceradar/`:
  - `baseline.py` – robust pre-event baselines using MAD (with fallback lookback)
  - `anomalies.py` – event-window deltas, %Δ, and z(MAD) + rule-based anomaly
  - `exposure.py` – reads IMERG raster (GeoTIFF/NetCDF) and samples at store points
  - `pipeline.py` – **coerces `store_id` types, normalizes `precip_mm_24h`, writes debug CSVs**
  - `mapviz.py` – Folium map of flagged rows
  - `io.py` – flexible CSV schema reader (accepts alternate column names)
- Runner: `scripts/run_priceradar.py` **always imports from local `src/`** (no need for `pip install -e .`)
- Example config: `configs/example_nyc.yml`
- Makefile targets and Dockerfile
- GitHub Actions CI workflow (`.github/workflows/ci.yml`)

---

## Requirements
- **Python**: 3.10+ (3.11 recommended)
- **Pip packages**: `pip install -r requirements.txt`
  - `pandas, numpy, geopandas, shapely, rasterio, rioxarray, xarray, folium, pyyaml, tqdm`
- **System libs** (Linux/Devcontainer/Codespaces usually OK already):
  - GDAL/GEOS/PROJ (needed by rasterio/geopandas)
  - On Debian/Ubuntu: `sudo apt-get install -y gdal-bin libgdal-dev libspatialindex-dev`

> In GitHub Codespaces with the provided devcontainer, these are typically preinstalled.

---

## Data inputs
You can point the pipeline at either:
1) **Remote CSVs (raw GitHub)** – simplest for now, _no env var needed_, or  
2) **Local clone / submodule** – use `${MANCINO_PATH}` env var in the YAML.

### Option 1 — Remote CSVs (recommended quick start)
Set your `configs/example_nyc.yml` like this:
```yaml
stores_csv: "https://raw.githubusercontent.com/jrmst102/mancino/refs/heads/main/data/v1_2025-09-21/stores.csv"
prices_csv: "https://raw.githubusercontent.com/jrmst102/mancino/refs/heads/main/data/v1_2025-09-21/daily_prices.csv"

# Event window (must lie within the data’s date range)
event_start: "2025-08-21"
event_end:   "2025-08-24"

# IMERG 24h accumulation raster (local file you provide)
imerg_path: "data/imerg_24h_accum.tif"

baseline_days: 28
precipitation_threshold_mm_24h: 50.0
alpha_zmad: 4.0
beta_pct: 0.25
crs_epsg: 4326
outdir: "out"
```

### Option 2 — Local clone or submodule
```bash
# submodule example
git submodule add https://github.com/jrmst102/mancino external/mancino
export MANCINO_PATH=$PWD/external/mancino
```
Then use paths like:
```yaml
stores_csv: "${MANCINO_PATH}/data/v1_2025-09-21/stores.csv"
prices_csv: "${MANCINO_PATH}/data/v1_2025-09-21/daily_prices.csv"
...
```

> If `daily_prices.csv` doesn’t exist, generate it from `transactions.csv` + `transaction_line_items.csv` (see snippet at the end).

---

## IMERG input (exposure layer)
You need a **24-hour precipitation accumulation raster** overlapping your stores for the chosen event window.

### Quick validation raster (constant 60 mm over NYC)
This lets you run end-to-end immediately:
```bash
mkdir -p data
python - <<'PY'
import os, numpy as np, rasterio as rio
from rasterio.transform import from_origin
os.makedirs("data", exist_ok=True)
width, height = 200, 200
lon_min, lat_max = -74.3, 41.0
res_x = (-73.5 - lon_min)/width
res_y = (lat_max - 40.4)/height
transform = from_origin(lon_min, lat_max, res_x, res_y)
data = np.full((height, width), 60.0, dtype="float32")  # 60 mm everywhere
with rio.open("data/imerg_24h_accum.tif","w",driver="GTiff",height=height,width=width,
              count=1,dtype="float32",crs="EPSG:4326",transform=transform) as dst:
    dst.write(data,1)
print("Wrote data/imerg_24h_accum.tif")
PY
```
Later, replace this with a real IMERG 24h accumulation for your dates (via NASA GES DISC/AppEEARS or a preprocessed GeoTIFF).

---

## Running the pipeline
```bash
# install Python deps
pip install -r requirements.txt

# run with your YAML config
python scripts/run_priceradar.py --config configs/example_nyc.yml
```

**Outputs:**
- `out/baseline_stats.csv` – per-(store,sku) baseline median & MAD
- `out/flags.csv` – anomalies + exposure + flags
- `out/map_flags.html` – interactive Folium map
- `out/_debug_anomalies.csv`, `out/_debug_stores.csv` – helpful for debugging

**Open the map:**
- **Codespaces/VS Code:** Right-click `out/map_flags.html` → *Open With…* → *Simple Browser* (or *Open Preview*).
- **Or** serve locally:
  ```bash
  python -m http.server 8000  # then open /out/map_flags.html
  ```

---

## Tuning & interpretation
- `baseline_days` – usually 28; must have data before `event_start`.
- `alpha_zmad` – robust z threshold (lower = more sensitive).
- `beta_pct` – percent change threshold (lower = more sensitive).
- `precipitation_threshold_mm_24h` – exposure gate; only flag where precip ≥ threshold.

Tips:
- If you get **no flags**, lower `alpha_zmad`, `beta_pct`, and/or the precip threshold.
- If many false positives, raise thresholds, add inventory/logistics context, or increase `baseline_days`.

---

## Troubleshooting

### ModuleNotFoundError: `priceradar`
The runner script forces imports from local `src/`, so this should not happen. If you call modules directly, use:
```bash
PYTHONPATH=src python scripts/run_priceradar.py --config configs/example_nyc.yml
```
Or install in editable mode (optional): create a `pyproject.toml` and `pip install -e .`

### FileNotFoundError: `${MANCINO_PATH}...`
Your YAML still references `${MANCINO_PATH}` but the env var isn’t exported. Either switch to the URL config or:
```bash
export MANCINO_PATH=/absolute/path/to/mancino
```

### ValueError: No price data in baseline window
Your `event_start` must have at least some history before it. Either move `event_start` earlier into your data window or reduce `baseline_days`.
The code also includes a **fallback**: if the primary window is too sparse, it expands lookback up to **180 days** and requires ≥3 observations per (store,sku).

### KeyError: `'precip_mm_24h' not in index`
Fixed in `pipeline.py`: the code now **normalizes precipitation column names**, coerces `store_id` types before merges, and guarantees `precip_mm_24h` exists.

### RasterioIOError: “No such file or directory” when writing GeoTIFF
Create the target folder first (e.g., `mkdir -p data`) or provide an absolute path in `imerg_path`.

### GDAL/GEOS/PROJ errors
Install system libs:
```bash
sudo apt-get update && sudo apt-get install -y gdal-bin libgdal-dev libspatialindex-dev
```

---

## Developer notes
- **Robust stats**: z(MAD) via 1.4826×MAD scaling; we clamp MAD to a small positive to avoid div-by-zero.
- **Type safety**: merges may fail silently if `store_id` is str vs int. The pipeline **coerces types** before merging.
- **Debug artifacts**: `_debug_anomalies.csv` and `_debug_stores.csv` help inspect columns and merges when tuning.

---

## Make targets
```bash
make install     # pip install -r requirements.txt
make run         # python scripts/run_priceradar.py --config configs/example_nyc.yml
make test        # runs the basic unit test
```

---

## Docker
```bash
docker build -t nasa_priceradar .
docker run --rm -it -v "$PWD":/app nasa_priceradar   python scripts/run_priceradar.py --config configs/example_nyc.yml
```

---

## (Optional) Generate daily_prices.csv inside Mancino
If needed, create daily median price per (store, sku, date) from transactions + line items:

```bash
python - <<'PY'
import os, pandas as pd
m = os.environ["MANCINO_PATH"]
tx = pd.read_csv(f"{m}/data/v1_2025-09-21/transactions.csv", parse_dates=["timestamp", "date"], infer_datetime_format=True)
if "date" not in tx.columns:
    tx["date"] = pd.to_datetime(tx["timestamp"]).dt.date
else:
    tx["date"] = pd.to_datetime(tx["date"]).dt.date
li = pd.read_csv(f"{m}/data/v1_2025-09-21/transaction_line_items.csv")
sku_col = "sku_id" if "sku_id" in li.columns else "product_id"
price_col = "unit_price" if "unit_price" in li.columns else ("price" if "price" in li.columns else None)
if price_col is None:
    raise SystemExit("Couldn't find a unit price column in line items (expected unit_price or price).")
li = li.merge(tx[["transaction_id","store_id","date"]], on="transaction_id", how="left")
li = li.dropna(subset=["store_id","date"])
daily = (li.groupby(["store_id", sku_col, "date"])[price_col]
           .median()
           .reset_index()
           .rename(columns={sku_col:"sku_id", price_col:"price"}))
daily["date"] = pd.to_datetime(daily["date"]).dt.date
out = f"{m}/data/v1_2025-09-21/daily_prices.csv"
daily.to_csv(out, index=False)
print("Wrote", out, "rows=", len(daily))
PY
```

---

## License
MIT
