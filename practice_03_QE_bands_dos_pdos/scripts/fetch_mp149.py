#!/usr/bin/env python3
"""Optional: fetch mp-149 from Materials Project and save a CIF."""
import os
from pathlib import Path
from mp_api.client import MPRester

api_key = os.environ.get("MP_API_KEY") or os.environ.get("PMG_MAPI_KEY")
if not api_key:
    raise SystemExit("Set MP_API_KEY (or PMG_MAPI_KEY) first.")

root = Path(__file__).resolve().parents[1]
out = root / "structure" / "mp-149_from_MP.cif"

with MPRester(api_key) as mpr:
    structure = mpr.get_structure_by_material_id("mp-149")

structure.to(filename=str(out))
print(out)
