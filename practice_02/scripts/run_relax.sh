#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p outputs tmp/relax_displaced

echo "=== RELAX: displaced Si atom at fixed cell ==="
mpirun -np "${NP:-2}" pw.x -in "inputs/si_relax_displaced.in" > "outputs/si_relax_displaced.out"

echo
echo "--- key output ---"
grep "!" "outputs/si_relax_displaced.out" | tail -n 3 || true
grep "Total force" "outputs/si_relax_displaced.out" | tail -n 5 || true
grep "P=" "outputs/si_relax_displaced.out" | tail -n 5 || true
grep "JOB DONE" "outputs/si_relax_displaced.out" | tail -n 1 || true
