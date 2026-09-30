#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from qe_helpers import read_vbm, pretty_label

root = Path(__file__).resolve().parents[1]
gnu = root / "results/bands/si_bands.dat.gnu"
labels_file = root / "generated/qe_bands_labels.tsv"
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

x = blocks[0][:,0]
vbm = read_vbm(scf_out)

label_indices, label_texts = [], []
with open(labels_file, encoding="utf-8") as f:
    next(f)
    for line in f:
        i0, i1, lin, lab = line.rstrip().split("\t")
        idx = int(i0)
        if idx < len(x):
            label_indices.append(idx)
            label_texts.append(pretty_label(lab))

plt.figure(figsize=(8.0, 5.2))
for b in blocks:
    plt.plot(b[:,0], b[:,1]-vbm, linewidth=1.0)

for idx in label_indices:
    plt.axvline(x[idx], linewidth=0.6)
plt.axhline(0.0, linewidth=0.8)

plt.xticks([x[i] for i in label_indices], label_texts)
plt.ylabel("Energy − VBM (eV)")
plt.xlabel("High-symmetry path")
plt.ylim(-12, 8)
plt.tight_layout()

out = root / "results/bands/si_bands.png"
plt.savefig(out, dpi=220)
print(out)
