#!/usr/bin/env python3
from pathlib import Path
import csv
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[2]
PLOTS=ROOT/'convergence'/'plots'
PLOTS.mkdir(parents=True,exist_ok=True)

def read_csv(path):
    rows=[]
    with path.open(encoding='utf-8') as f:
        for r in csv.DictReader(f):
            if r['job_done']!='yes' or not r['energy_Ry']:
                continue
            rows.append(r)
    return rows

def save_plot(x,y,xlabel,ylabel,name):
    plt.figure(figsize=(7,4.5))
    plt.plot(x,y,'o-')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True,alpha=0.3)
    plt.tight_layout()
    path=PLOTS/name
    plt.savefig(path,dpi=180)
    plt.close()
    print('saved',path)

e=read_csv(ROOT/'convergence'/'ecut_convergence.csv')
if e:
    x=[float(r['ecutwfc_Ry']) for r in e]
    save_plot(x,[float(r['energy_Ry']) for r in e],'ecutwfc (Ry)','Total energy (Ry)','ecut_total_energy.png')
    save_plot(x,[float(r['deltaE_meV_per_atom_vs_last']) for r in e],'ecutwfc (Ry)',r'$\Delta E$ vs last point (meV/atom)','ecut_delta_meV_per_atom.png')

k=read_csv(ROOT/'convergence'/'kgrid_convergence.csv')
if k:
    x=[int(r['k1']) for r in k]
    save_plot(x,[float(r['energy_Ry']) for r in k],'N for N x N x N k-grid','Total energy (Ry)','kgrid_total_energy.png')
    save_plot(x,[float(r['deltaE_meV_per_atom_vs_last']) for r in k],'N for N x N x N k-grid',r'$\Delta E$ vs last point (meV/atom)','kgrid_delta_meV_per_atom.png')
