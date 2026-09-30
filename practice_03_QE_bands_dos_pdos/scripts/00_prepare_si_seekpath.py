#!/usr/bin/env python3
"""Prepare standardized primitive Si structure and QE inputs for practice 3.

Core idea: one structure -> three k-point tasks:
  uniform mesh       -> SCF charge density
  high-symmetry path -> bands E_n(k)
  dense uniform mesh -> DOS / PDOS

The main bands input uses human-readable K_POINTS crystal_b.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import os

import seekpath
from pymatgen.core import Structure, Element


def fmt_vec(v):
    return " ".join(f"{x: .12f}" for x in v)


def qe_structure_block(structure: Structure) -> str:
    lines = ["CELL_PARAMETERS angstrom"]
    for v in structure.lattice.matrix:
        lines.append(fmt_vec(v))
    lines.append("")
    lines.append("ATOMIC_POSITIONS crystal")
    for site in structure:
        x, y, z = site.frac_coords
        lines.append(f"{site.specie.symbol:2s} {x: .12f} {y: .12f} {z: .12f}")
    return "\n".join(lines)


def qe_header(calculation, outdir, pseudo_dir, pseudo_file, structure, nbnd=None, occupations="fixed"):
    nbnd_line = f"  nbnd = {nbnd}\n" if nbnd is not None else ""
    return f"""&CONTROL
  calculation = '{calculation}'
  prefix = 'si'
  pseudo_dir = '{pseudo_dir}'
  outdir = '{outdir}'
  tstress = .true.
  tprnfor = .true.
/
&SYSTEM
  ibrav = 0
  nat = {len(structure)}
  ntyp = 1
  ecutwfc = 40.0
  ecutrho = 160.0
{nbnd_line}  occupations = '{occupations}'
/
&ELECTRONS
  conv_thr = 1.0d-10
  mixing_beta = 0.7
/
ATOMIC_SPECIES
Si 28.0855 {pseudo_file}

{qe_structure_block(structure)}
"""


def pretty_label(label: str) -> str:
    return "GAMMA" if label in ["GAMMA", "Γ", "Gamma"] else label


def make_crystal_b(point_coords, path, n_per_segment=50):
    entries = []
    previous_end = None
    for start, end in path:
        start = pretty_label(start)
        end = pretty_label(end)
        if previous_end is None:
            entries.append([start, n_per_segment])
        elif start != previous_end:
            entries[-1][1] = 1
            entries.append([start, n_per_segment])
        entries.append([end, n_per_segment])
        previous_end = end
    if entries:
        entries[-1][1] = 1
    lines = ["K_POINTS crystal_b", str(len(entries))]
    label_rows = []
    cumulative = 0
    for i, (label, npoints) in enumerate(entries):
        k = point_coords[label]
        lines.append(f"{k[0]: .10f} {k[1]: .10f} {k[2]: .10f} {int(npoints):3d}  ! {label}")
        label_rows.append((i, cumulative, label))
        cumulative += max(int(npoints), 1)
    return "\n".join(lines), label_rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cif", help="Input CIF")
    p.add_argument("--pseudo-dir", default=os.environ.get("QE_PSEUDO_DIR", "/home/md/Software/qe-7.5/pseudo"))
    p.add_argument("--pseudo-file", default=os.environ.get("QE_PSEUDO_FILE", "Si_r.upf"))
    p.add_argument("--scf-grid", type=int, default=6)
    p.add_argument("--dos-grid", type=int, default=20)
    p.add_argument("--bands-points", type=int, default=50)
    p.add_argument("--nbnd", type=int, default=20)
    p.add_argument("--reference-distance", type=float, default=0.03)
    p.add_argument("--dos-occupations", default="tetrahedra", choices=["fixed", "tetrahedra"])
    args = p.parse_args()

    root = Path(__file__).resolve().parents[1]
    inputs = root / "inputs"
    generated = root / "generated"
    inputs.mkdir(exist_ok=True)
    generated.mkdir(exist_ok=True)

    s = Structure.from_file(args.cif)
    sp_in = (s.lattice.matrix, s.frac_coords, [site.specie.Z for site in s])

    res = seekpath.get_path(sp_in, with_time_reversal=True, symprec=1.0e-5)
    explicit = seekpath.get_explicit_k_path(sp_in, with_time_reversal=True,
                                            reference_distance=args.reference_distance,
                                            symprec=1.0e-5)

    primitive = Structure(lattice=res["primitive_lattice"],
                          species=[Element.from_Z(int(z)) for z in res["primitive_types"]],
                          coords=res["primitive_positions"],
                          coords_are_cartesian=False)
    primitive.to(filename=str(generated / "si_seekpath_primitive.cif"))

    point_coords = {pretty_label(k): v for k, v in res["point_coords"].items()}
    path = [(pretty_label(a), pretty_label(b)) for a, b in res["path"]]

    with open(generated / "seekpath_summary.txt", "w", encoding="utf-8") as f:
        f.write(f"bravais_lattice = {res['bravais_lattice']}\n")
        f.write(f"bravais_lattice_extended = {res['bravais_lattice_extended']}\n\n")
        f.write("High-symmetry points (fractional reciprocal coordinates):\n")
        for label, xyz in point_coords.items():
            f.write(f"{label:10s} {xyz[0]: .8f} {xyz[1]: .8f} {xyz[2]: .8f}\n")
        f.write("\nRecommended path:\n")
        for start, stop in path:
            f.write(f"{start} -> {stop}\n")

    scf = qe_header("scf", "./tmp/scf", args.pseudo_dir, args.pseudo_file, primitive)
    scf += f"""
K_POINTS automatic
{args.scf_grid} {args.scf_grid} {args.scf_grid} 1 1 1
"""
    (inputs / "si_scf.in").write_text(scf, encoding="utf-8")

    bands = qe_header("bands", "./tmp/bands", args.pseudo_dir, args.pseudo_file, primitive, nbnd=args.nbnd)
    crystal_b, label_rows = make_crystal_b(point_coords, path, n_per_segment=args.bands_points)
    bands += "\n" + crystal_b + "\n"
    (inputs / "si_bands.in").write_text(bands, encoding="utf-8")

    with open(generated / "qe_bands_labels.tsv", "w", encoding="utf-8") as f:
        f.write("# row_index\tapprox_k_index\tlabel\n")
        for row_index, approx_idx, label in label_rows:
            f.write(f"{row_index}\t{approx_idx}\t{label}\n")

    with open(generated / "K_POINTS_seekpath_explicit.dat", "w", encoding="utf-8") as f:
        kpoints = explicit["explicit_kpoints_rel"]
        labels = explicit["explicit_kpoints_labels"]
        f.write("K_POINTS crystal\n")
        f.write(f"{len(kpoints)}\n")
        for k, label in zip(kpoints, labels):
            lab = f" ! {pretty_label(label)}" if label else ""
            f.write(f"{k[0]: .10f} {k[1]: .10f} {k[2]: .10f} 1.0{lab}\n")

    nscf = qe_header("nscf", "./tmp/dos", args.pseudo_dir, args.pseudo_file, primitive,
                     nbnd=args.nbnd, occupations=args.dos_occupations)
    nscf += f"""
K_POINTS automatic
{args.dos_grid} {args.dos_grid} {args.dos_grid} 1 1 1
"""
    (inputs / "si_nscf_dos.in").write_text(nscf, encoding="utf-8")

    (inputs / "si_bands_pp.in").write_text("""&BANDS
  prefix = 'si'
  outdir = './tmp/bands'
  filband = './results/bands/si_bands.dat'
/
""", encoding="utf-8")

    (inputs / "si_dos_pp.in").write_text("""&DOS
  prefix = 'si'
  outdir = './tmp/dos'
  fildos = './results/dos/si.dos'
  bz_sum = 'tetrahedra'
  DeltaE = 0.02
/
""", encoding="utf-8")

    (inputs / "si_projwfc_dos.in").write_text("""&PROJWFC
  prefix = 'si'
  outdir = './tmp/dos'
  filpdos = './results/dos/si'
  DeltaE = 0.02
/
""", encoding="utf-8")

    print("Prepared:")
    for name in ["si_scf.in", "si_bands.in", "si_nscf_dos.in", "si_bands_pp.in", "si_dos_pp.in", "si_projwfc_dos.in"]:
        print("  inputs/" + name)
    print("  generated/si_seekpath_primitive.cif")
    print("  generated/seekpath_summary.txt")
    print("  generated/qe_bands_labels.tsv")
    print("  generated/K_POINTS_seekpath_explicit.dat")
    print()
    print("Three k-point roles:")
    print(f"  SCF  : {args.scf_grid}x{args.scf_grid}x{args.scf_grid} shifted uniform mesh")
    print("  bands: human-readable K_POINTS crystal_b from SeeK-path")
    print(f"  DOS  : {args.dos_grid}x{args.dos_grid}x{args.dos_grid} shifted dense uniform mesh")
    print(f"  nbnd : {args.nbnd}")
    print(f"  DOS occupations: {args.dos_occupations}")

if __name__ == "__main__":
    main()
