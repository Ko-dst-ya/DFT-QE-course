#!/usr/bin/env python3
from pathlib import Path
import re, csv

ROOT = Path(__file__).resolve().parents[2]
RY_TO_EV = 13.605693122994
NAT = 2

RE_E = re.compile(r"!\s+total energy\s+=\s+([-+0-9.Ee]+)\s+Ry")
RE_F = re.compile(r"Total force\s+=\s+([-+0-9.Ee]+)")
RE_P = re.compile(r"P=\s*([-+0-9.Ee]+)")
RE_ECUT = re.compile(r"ecutwfc\s*=\s*([-+0-9.Ee]+)", re.I)
RE_K = re.compile(r"K_POINTS\s+automatic\s*\n\s*(\d+)\s+(\d+)\s+(\d+)", re.I)

def last(pattern, text):
    m=pattern.findall(text)
    return float(m[-1]) if m else None

def parse_pair(inp,out):
    it=inp.read_text(errors='replace')
    ot=out.read_text(errors='replace')
    e=last(RE_E,ot)
    force=last(RE_F,ot)
    pressure=last(RE_P,ot)
    ec=RE_ECUT.search(it)
    km=RE_K.search(it)
    return {
        'job_done': 'yes' if 'JOB DONE' in ot else 'no',
        'energy_Ry': e,
        'energy_eV_per_atom': (e*RY_TO_EV/NAT if e is not None else None),
        'total_force_Ry_Bohr': force,
        'pressure_kbar': pressure,
        'ecutwfc_Ry': float(ec.group(1)) if ec else None,
        'k1': int(km.group(1)) if km else None,
        'k2': int(km.group(2)) if km else None,
        'k3': int(km.group(3)) if km else None,
    }

def write_case(kind):
    idir=ROOT/'convergence'/kind/'inputs'
    odir=ROOT/'convergence'/kind/'outputs'
    rows=[]
    for inp in sorted(idir.glob('*.in')):
        out=odir/(inp.stem+'.out')
        if not out.exists():
            print('missing:',out)
            continue
        r=parse_pair(inp,out)
        r['case']=inp.stem
        rows.append(r)
    if not rows:
        print('No outputs for',kind)
        return
    key='ecutwfc_Ry' if kind=='ecut' else 'k1'
    rows.sort(key=lambda x: x[key])
    ref=next((r['energy_eV_per_atom'] for r in reversed(rows) if r['energy_eV_per_atom'] is not None),None)
    for r in rows:
        r['deltaE_meV_per_atom_vs_last']=(1000*(r['energy_eV_per_atom']-ref) if ref is not None and r['energy_eV_per_atom'] is not None else None)
    outcsv=ROOT/'convergence'/f'{kind}_convergence.csv'
    fields=['case','job_done','ecutwfc_Ry','k1','k2','k3','energy_Ry','energy_eV_per_atom','deltaE_meV_per_atom_vs_last','total_force_Ry_Bohr','pressure_kbar']
    with outcsv.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print('wrote',outcsv)

write_case('ecut')
write_case('kgrid')
