#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
mkdir -p outputs tmp/vc_relax_wrong_a

echo "=== VC-RELAX: optimize cubic-cell volume ==="
mpirun -np "${NP:-2}" pw.x -in "inputs/si_vc_relax_wrong_a.in" > "outputs/si_vc_relax_wrong_a.out"

echo
echo "--- key output ---"
grep "!" "outputs/si_vc_relax_wrong_a.out" | tail -n 3 || true
grep "Total force" "outputs/si_vc_relax_wrong_a.out" | tail -n 5 || true
grep "P=" "outputs/si_vc_relax_wrong_a.out" | tail -n 5 || true
grep "JOB DONE" "outputs/si_vc_relax_wrong_a.out" | tail -n 1 || true
