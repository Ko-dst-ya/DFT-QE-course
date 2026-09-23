#!/usr/bin/env python3
from pathlib import Path
import re, math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"

RE_E = re.compile(r"!\s+total energy\s+=\s+([-+0-9.Ee]+)\s+Ry")
RE_F = re.compile(r"Total force\s+=\s+([-+0-9.Ee]+)")
RE_P = re.compile(r"P=\s*([-+0-9.Ee]+)")

def last_float(pattern, text):
    vals = pattern.findall(text)
    return float(vals[-1]) if vals else None

def final_cell_angstrom(text):
    lines = text.splitlines()
    for i in range(len(lines)-1, -1, -1):
        if "CELL_PARAMETERS" in lines[i] and "angstrom" in lines[i].lower():
            try:
                vecs=[]
                for j in range(i+1,i+4):
                    vecs.append([float(x) for x in lines[j].split()[:3]])
                return vecs
            except Exception:
                return None
    return None

def conventional_a_from_primitive(vecs):
    if not vecs:
        return None
    l=math.sqrt(sum(x*x for x in vecs[0]))
    return math.sqrt(2.0)*l

files=[
    "si_scf_wrong_a.out",
    "si_relax_displaced.out",
    "si_vc_relax_wrong_a.out",
]
for fn in files:
    p=OUT/fn
    print(f"\n=== {fn} ===")
    if not p.exists():
        print("not found")
        continue
    txt=p.read_text(errors="replace")
    e=last_float(RE_E,txt)
    f=last_float(RE_F,txt)
    pr=last_float(RE_P,txt)
    print("JOB DONE:", "yes" if "JOB DONE" in txt else "no")
    print("final energy (Ry):", e)
    print("final total force (Ry/Bohr):", f)
    print("final pressure (kbar):", pr)
    vecs=final_cell_angstrom(txt)
    a=conventional_a_from_primitive(vecs)
    if a is not None:
        print(f"final conventional cubic a (A): {a:.6f}")
