#!/usr/bin/env python3
"""
Parse the human-readable projwfc.x output for a non-spin-polarized calculation.

For each KS state (band, k), projwfc.x prints weights such as
    0.123*[# 2]
where #2 refers to an atomic state listed near the top of the output.
This script groups those weights by angular momentum l:
    l=0 -> s, l=1 -> p, l=2 -> d, l=3 -> f.
"""
from pathlib import Path
import re, csv

root = Path(__file__).resolve().parents[1]
inp = root / "outputs/02_projwfc_bands.out"
out = root / "results/bands/si_projected_bands.csv"

text = inp.read_text(errors="ignore").splitlines()

state_l = {}
state_re = re.compile(r"state\s*#\s*(\d+):.*?\(l\s*=\s*(\d+)\b", re.I)
for line in text:
    m = state_re.search(line)
    if m:
        state_l[int(m.group(1))] = int(m.group(2))

if not state_l:
    raise RuntimeError("Could not parse atomic projection state definitions.")

energy_re = re.compile(r"e\(\s*(\d+)\s*\)\s*=\s*([-+0-9.EeDd]+)\s*eV", re.I)
k_re = re.compile(r"^\s*k\s*=", re.I)
coef_re = re.compile(r"([-+0-9.EeDd]+)\s*\*\s*\[#\s*(\d+)\s*\]")

rows = []
k_index = -1
i = 0
while i < len(text):
    line = text[i]
    if k_re.search(line):
        k_index += 1
        i += 1
        continue
    em = energy_re.search(line)
    if em:
        band = int(em.group(1))
        energy = float(em.group(2).replace("D","E").replace("d","e"))
        chunk = []
        i += 1
        while i < len(text):
            if energy_re.search(text[i]) or k_re.search(text[i]):
                break
            chunk.append(text[i])
            if "|psi|^2" in text[i].replace(" ",""):
                i += 1
                break
            # typical projection text is short; stop at blank after psi block
            if chunk and not text[i].strip() and any("psi" in q for q in chunk):
                i += 1
                break
            i += 1

        weights = {0:0.0, 1:0.0, 2:0.0, 3:0.0}
        for c in chunk:
            for val, st in coef_re.findall(c):
                state = int(st)
                l = state_l.get(state)
                if l in weights:
                    weights[l] += float(val.replace("D","E").replace("d","e"))

        rows.append({
            "k_index0": k_index,
            "band": band,
            "energy_eV": energy,
            "s_weight": weights[0],
            "p_weight": weights[1],
            "d_weight": weights[2],
            "f_weight": weights[3],
            "spdf_sum": sum(weights.values()),
        })
        continue
    i += 1

if not rows:
    raise RuntimeError("No projected band states parsed. Inspect outputs/02_projwfc_bands.out.")

with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys())
    w.writeheader()
    w.writerows(rows)

print(f"{out}  ({len(rows)} states)")
