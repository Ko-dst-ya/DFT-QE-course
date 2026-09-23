# Practice 02 — SCF, forces/stress, relax/vc-relax, convergence

This directory is designed for the second Quantum ESPRESSO practical.

## Physical storyline

1. `si_scf_wrong_a.in`: perfect diamond Si at `a = 5.30 Å`.
   By symmetry the atomic forces should be very small, while the pressure/stress need not be zero.
2. `si_relax_displaced.in`: one Si atom is displaced at fixed cell.
   `relax` optimizes internal coordinates.
3. `si_vc_relax_wrong_a.in`: perfect diamond Si at the same deliberately wrong lattice parameter.
   `vc-relax` changes the volume and should approach the equilibrium lattice parameter.

Reference from Practice 1 fit: `a0 ≈ 5.469653 Å`.

## Pseudopotential

All inputs currently use:

`/home/md/Software/qe-7.5/pseudo/Si_r.upf`

If your installation uses another location, edit `pseudo_dir` in the input files before running.

## Quick run

```bash
bash scripts/run_scf.sh
bash scripts/run_relax.sh
bash scripts/run_vcrelax.sh
python scripts/analyze_outputs.py
```

The environment variable `NP` changes the number of MPI ranks, e.g. `NP=4 bash scripts/run_scf.sh`.

## Convergence tests

### Wavefunction cutoff

`convergence/ecut/` uses `ecutwfc = 20, 25, 30, 35, 40, 50, 60 Ry` and sets `ecutrho = 4*ecutwfc`.
The k-grid is fixed at `6x6x6`, shifted.

### k-grid

`convergence/kgrid/` uses `2x2x2` through `10x10x10` shifted meshes.
The cutoff is fixed at `ecutwfc = 50 Ry`, `ecutrho = 200 Ry` to reduce basis-set error while testing k-point convergence.

Run everything:

```bash
bash convergence/run_all.sh
```

Then inspect:

- `convergence/ecut_convergence.csv`
- `convergence/kgrid_convergence.csv`
- `convergence/plots/*.png`

The plots include total energy and ΔE relative to the densest/highest setting in meV/atom.

## Important

A calculation that reaches `JOB DONE` is not automatically numerically converged. Convergence must be checked for the quantity of interest. For `vc-relax`, stress/pressure convergence can matter even when total energy already looks stable.

Official QE 7.5 `pw.x` input reference:
https://www.quantum-espresso.org/Doc/INPUT_PW.html
