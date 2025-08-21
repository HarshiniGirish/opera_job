from pathlib import Path
import os, shutil

base_dir = Path(__file__).resolve().parent
out_dir = base_dir / "output"     # relative folder that DPS collects
out_dir.mkdir(parents=True, exist_ok=True)

cog_path = out_dir / "disp_masked_subset.cog.tif"
final_path = save_cog(disp_sub, str(cog_path), tile=256, compress="DEFLATE", predictor=2)

# optional ADE convenience copy
if os.path.isdir("/projects"):
    user = os.environ.get("USER") or os.environ.get("PUSER") or "jobuser"
    shutil.copy(str(final_path), f"/projects/{user}_disp_masked_subset.cog.tif")
def save_cog(da: xr.DataArray, out_path: str,
             nodata_val: float = -9999.0,
             tile: int = 256,
             compress: str = "DEFLATE",
             predictor: int = 2,
             overview_resampling: str = "average") -> str:
    # Ensure 2D
    if "time" in da.dims:
        da = da.isel(time=0)

    da = da.rio.write_nodata(nodata_val, inplace=False)
    arr = da.values
    arr_out = np.where(np.isnan(arr), nodata_val, arr).astype("float32")

    # Try direct COG
    try:
        da_cog = xr.DataArray(
            arr_out, dims=da.dims,
            coords={k: da.coords[k] for k in da.dims if k in da.coords},
            attrs=da.attrs,
        ).rio.write_crs(da.rio.crs, inplace=False).rio.write_transform(da.rio.transform(), inplace=False)
        da_cog.rio.to_raster(
            out_path,
            driver="COG",
            dtype="float32",
            nodata=nodata_val,
            blockxsize=tile, blockysize=tile,
            compress=compress, predictor=predictor,
            overview_resampling=overview_resampling,
            BIGTIFF="IF_NEEDED",
        )
        print(f"[cog] wrote COG directly: {out_path}")
        return out_path
    except Exception as e:
        print(f"[cog] direct COG path not available ({e}); falling back to GeoTIFF + overviews…")

    # Fallback: tiled GTiff + overviews then convert
    tmp = out_path + ".tmp.tif"
    profile = {
        "driver": "GTiff",
        "height": arr_out.shape[0], "width": arr_out.shape[1],
        "count": 1, "dtype": "float32",
        "crs": da.rio.crs, "transform": da.rio.transform(),
        "nodata": nodata_val, "tiled": True,
        "blockxsize": tile, "blockysize": tile,
        "compress": compress, "predictor": predictor,
        "BIGTIFF": "IF_NEEDED",
    }
    with rasterio.open(tmp, "w", **profile) as dst:
        dst.write(arr_out, 1)
        factors = [2, 4, 8, 16, 32]
        dst.build_overviews(factors, getattr(Resampling, overview_resampling))
        dst.update_tags(ns="rio_overview", resampling=overview_resampling)

    try:
        rio_copy(
            tmp, out_path,
            copy_src_overviews=True, driver="COG",
            compress=compress, predictor=predictor,
            BIGTIFF="IF_NEEDED", nodata=nodata_val,
            overview_resampling=overview_resampling,
        )
        os.remove(tmp)
        print(f"[cog] converted to COG: {out_path}")
    except Exception as e:
        print(f"[cog] could not convert to COG ({e}); kept tiled GeoTIFF at: {tmp}")
        return tmp

    return out_path
