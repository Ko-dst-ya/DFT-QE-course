#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/../.." && pwd)"
cd "$ROOT_DIR"
mkdir -p convergence/ecut/outputs tmp

for f in convergence/ecut/inputs/si_ecut_*.in; do
  base="$(basename "${f%.in}")"
  echo "=== Running $base ==="
  mpirun -np "${NP:-2}" pw.x -in "$f" > "convergence/ecut/outputs/${base}.out"
  grep "!" "convergence/ecut/outputs/${base}.out" | tail -n 1 || true
  grep "P=" "convergence/ecut/outputs/${base}.out" | tail -n 1 || true
done

echo "Finished ecut sweep."
