#!/usr/bin/env python3
from pathlib import Path
import re
import numpy as np
import matplotlib.pyplot as plt
from qe_helpers import read_vbm

root = Path(__file__).resolve().parents[1]
dos_dir = root / "results/dos"
scf_out = root / "outputs/01_scf.out"
band_edges = root / "results/bands/si_band_edges.txt"

# Prefer the VBM extracted from the actual band path (which contains Γ for Si).
# A shifted SCF mesh may miss Γ and place "highest occupied level" slightly too low.
if band_edges.exists():
    text = band_edges.read_text(errors="ignore")
    m = re.search(r"VBM_eV\s*=\s*([-+0-9.Ee]+)", text)
    if not m:
        raise RuntimeError(f"Could not parse VBM from {band_edges}")
    vbm = float(m.group(1))
else:
    vbm = read_vbm(scf_out)
    print("WARNING: band-path VBM not found; using highest occupied level from SCF output.")

total_file = dos_dir / "si.dos"
if not total_file.exists():
    raise SystemExit("Missing results/dos/si.dos. Run scripts/03_dos_pdos.sh first.")

total = np.loadtxt(total_file, comments="#")
E = total[:,0] - vbm
DOS = total[:,1]

def sum_channel(letter):
    files = [p for p in dos_dir.glob("si.pdos_atm*") if f"({letter})" in p.name]
    if not files:
        return None
    acc = None
    e0 = None
    for p in files:
        arr = np.loadtxt(p, comments="#")
        if e0 is None:
            e0 = arr[:,0]
            acc = np.zeros_like(e0)
        # Col 2 (index 1) is LDOS summed over m for spin-unpolarized QE output.
        acc += arr[:,1]
    return e0 - vbm, acc

s = sum_channel("s")
p = sum_channel("p")

plt.figure(figsize=(6.4, 5.0))
plt.plot(E, DOS, label="Total DOS")
if s is not None:
    plt.plot(s[0], s[1], label="Si s")
if p is not None:
    plt.plot(p[0], p[1], label="Si p")
plt.axvline(0.0, linewidth=0.8)
plt.xlabel("Energy − VBM (eV)")
plt.ylabel("DOS (states/eV)")
plt.xlim(-12, 8)
plt.legend()
plt.tight_layout()

out = dos_dir / "si_DOS_PDOS_sp.png"
plt.savefig(out, dpi=220)
print(out)
print(f"Energy zero: VBM = {vbm:.6f} eV")
