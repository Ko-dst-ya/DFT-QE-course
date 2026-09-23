#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/../.." && pwd)"
cd "$ROOT_DIR"
mkdir -p convergence/kgrid/outputs tmp

for f in convergence/kgrid/inputs/si_k_*.in; do
  base="$(basename "${f%.in}")"
  echo "=== Running $base ==="
  mpirun -np "${NP:-2}" pw.x -in "$f" > "convergence/kgrid/outputs/${base}.out"
  grep "!" "convergence/kgrid/outputs/${base}.out" | tail -n 1 || true
  grep "P=" "convergence/kgrid/outputs/${base}.out" | tail -n 1 || true
done

echo "Finished k-grid sweep."
