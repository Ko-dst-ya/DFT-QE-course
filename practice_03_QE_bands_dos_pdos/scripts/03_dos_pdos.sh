#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
NP="${NP:-2}"

if [[ ! -d tmp/scf/si.save ]]; then
  echo "ERROR: run bash scripts/01_scf.sh first."
  exit 1
fi

mkdir -p outputs results/dos tmp
rm -rf tmp/dos
mkdir -p tmp/dos
cp -a tmp/scf/si.save tmp/dos/

echo "[NSCF] dense uniform k-mesh -> many eigenvalues for DOS integration"
echo "Default input uses occupations='tetrahedra', nbnd=20, and 20x20x20 k-grid."
mpirun -np "$NP" pw.x -in inputs/si_nscf_dos.in > outputs/03_nscf_dos.out

echo "[dos.x] total DOS"
dos.x -in inputs/si_dos_pp.in > outputs/03_dos_x.out

echo "[projwfc.x] projected DOS (PDOS)"
projwfc.x -in inputs/si_projwfc_dos.in > outputs/03_projwfc_dos.out

python scripts/plot_dos_pdos.py

echo
echo "Created:"
ls -1 results/dos
