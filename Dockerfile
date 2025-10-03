# Lightweight runtime for nasa_priceradar
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System deps for geopandas/rasterio
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev libspatialindex-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["python", "scripts/run_priceradar.py", "--config", "configs/example_nyc.yml"]
