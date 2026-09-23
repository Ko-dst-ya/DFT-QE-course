#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p outputs tmp/scf_wrong_a

echo "=== SCF: wrong lattice parameter, perfect diamond symmetry ==="
mpirun -np "${NP:-2}" pw.x -in "inputs/si_scf_wrong_a.in" > "outputs/si_scf_wrong_a.out"

echo
echo "--- key output ---"
grep "!" "outputs/si_scf_wrong_a.out" | tail -n 3 || true
grep "Total force" "outputs/si_scf_wrong_a.out" | tail -n 5 || true
grep "P=" "outputs/si_scf_wrong_a.out" | tail -n 5 || true
grep "JOB DONE" "outputs/si_scf_wrong_a.out" | tail -n 1 || true
