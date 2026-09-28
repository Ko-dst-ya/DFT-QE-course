#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
NP="${NP:-2}"

mkdir -p outputs results tmp
rm -rf tmp/scf
mkdir -p tmp/scf

echo "[SCF] uniform k-mesh -> self-consistent charge density"
mpirun -np "$NP" pw.x -in inputs/si_scf.in > outputs/01_scf.out

echo
grep "!" outputs/01_scf.out | tail -1 || true
grep -i "highest occupied" outputs/01_scf.out | tail -1 || true
grep "JOB DONE" outputs/01_scf.out | tail -1 || true
