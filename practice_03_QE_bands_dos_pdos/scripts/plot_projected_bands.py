#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt
from qe_helpers import read_vbm, pretty_label

root = Path(__file__).resolve().parents[1]
gnu = root / "results/bands/si_bands.dat.gnu"
csvfile = root / "results/bands/si_projected_bands.csv"
labels_file = root / "generated/seekpath_labels.tsv"
scf_out = root / "outputs/01_scf.out"

# Parse bands.x GNU file.
blocks, cur = [], []
for line in gnu.read_text().splitlines():
    if not line.strip():
        if cur:
            blocks.append(np.array(cur, float))
            cur = []
        continue
    p = line.split()
    if len(p) >= 2:
        cur.append((float(p[0]), float(p[1])))
if cur:
    blocks.append(np.array(cur, float))

x = blocks[0][:,0]
vbm = read_vbm(scf_out)

labels = []
with open(labels_file, encoding="utf-8") as f:
    next(f)
    for line in f:
        i0, i1, lin, lab = line.rstrip().split("\t")
        idx = int(i0)
        if idx < len(x):
            labels.append((idx, pretty_label(lab)))

rows = []
with open(csvfile, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append({
            "k": int(r["k_index0"]),
            "band": int(r["band"]),
            "E": float(r["energy_eV"]) - vbm,
            "s": float(r["s_weight"]),
            "p": float(r["p_weight"]),
        })

for orbital, col in [("s", "s"), ("p", "p")]:
    plt.figure(figsize=(8.0, 5.2))
    for b in blocks:
        plt.plot(b[:,0], b[:,1]-vbm, linewidth=0.7)

    xs, es, ws = [], [], []
    for r in rows:
        if 0 <= r["k"] < len(x) and r[col] > 1e-4:
            xs.append(x[r["k"]])
            es.append(r["E"])
            ws.append(r[col])

    if xs:
        sizes = 75.0 * np.sqrt(np.array(ws))
        plt.scatter(xs, es, s=sizes, alpha=0.55)

    for idx, lab in labels:
        plt.axvline(x[idx], linewidth=0.5)
    plt.axhline(0.0, linewidth=0.8)
    plt.xticks([x[i] for i,_ in labels], [lab for _,lab in labels])
    plt.ylabel("Energy − VBM (eV)")
    plt.xlabel(f"High-symmetry path — marker size ∝ {orbital} weight")
    plt.ylim(-12, 8)
    plt.tight_layout()
    out = root / f"results/bands/si_bands_{orbital}_projected.png"
    plt.savefig(out, dpi=220)
    print(out)
