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
