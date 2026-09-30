#!/usr/bin/env python3
from pathlib import Path
import re
import numpy as np
import matplotlib.pyplot as plt
from qe_helpers import read_vbm, pretty_label

root = Path(__file__).resolve().parents[1]
gnu = root / "results/bands/si_bands.dat.gnu"
labels_file = root / "generated/qe_bands_labels.tsv"
bands_x_out = root / "outputs/02_bands_x.out"
scf_out = root / "outputs/01_scf.out"

if not gnu.exists():
    raise SystemExit("Missing results/bands/si_bands.dat.gnu. Run scripts/02_bands.sh first.")

# bands.x .gnu: one x,E block per band separated by blank lines.
blocks = []
current = []
for line in gnu.read_text().splitlines():
    if not line.strip():
        if current:
            blocks.append(np.array(current, float))
            current = []
        continue
    parts = line.split()
    if len(parts) >= 2:
        current.append((float(parts[0]), float(parts[1])))
if current:
    blocks.append(np.array(current, float))

if not blocks:
    raise RuntimeError("No band blocks parsed from .gnu file.")

vbm = read_vbm(scf_out)

# Labels are stored in the same order as the special points in K_POINTS crystal_b.
labels = []
with open(labels_file, encoding="utf-8") as f:
    for line in f:
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.rstrip().split("\t")
        labels.append(pretty_label(parts[-1]))

# bands.x prints the actual x-coordinate of every high-symmetry point.
# Use those coordinates directly instead of reconstructing indices ourselves.
tick_x = []
if bands_x_out.exists():
    pattern = re.compile(r"high-symmetry point:.*?x coordinate\s+([-+0-9.Ee]+)", re.I)
    for line in bands_x_out.read_text(errors="ignore").splitlines():
        m = pattern.search(line)
        if m:
            tick_x.append(float(m.group(1)))

if len(tick_x) < len(labels):
    raise RuntimeError(
        f"Found {len(tick_x)} high-symmetry x-coordinates in {bands_x_out}, "
        f"but {len(labels)} labels in {labels_file}."
    )

tick_x = tick_x[:len(labels)]

# Combine discontinuous points that share the same plotting coordinate, e.g. U|K.
merged_x = []
merged_labels = []
for xval, lab in zip(tick_x, labels):
    if merged_x and abs(xval - merged_x[-1]) < 1e-8:
        merged_labels[-1] = merged_labels[-1] + "|" + lab
    else:
        merged_x.append(xval)
        merged_labels.append(lab)

plt.figure(figsize=(8.0, 5.2))
for b in blocks:
    plt.plot(b[:, 0], b[:, 1] - vbm, linewidth=1.0)

for xval in merged_x:
    plt.axvline(xval, linewidth=0.6)
plt.axhline(0.0, linewidth=0.8)

plt.xticks(merged_x, merged_labels)
plt.ylabel("Energy − VBM (eV)")
plt.xlabel("High-symmetry path")
plt.ylim(-12, 8)
plt.tight_layout()

out = root / "results/bands/si_bands.png"
plt.savefig(out, dpi=220)
print(out)
