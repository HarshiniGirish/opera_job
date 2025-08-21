# !/bin/bash
set -euo pipefail

# show the exact python we'll use
python -V
python -m pip --version

# keep tooling current
python -m pip install --upgrade --no-cache-dir pip setuptools wheel

# runtime deps
python -m pip install --no-cache-dir \
  numpy \
  boto3 \
  xarray \
  rioxarray \
  rasterio \
  shapely \
  pyproj \
  affine \
  h5netcdf \
  maap-py
