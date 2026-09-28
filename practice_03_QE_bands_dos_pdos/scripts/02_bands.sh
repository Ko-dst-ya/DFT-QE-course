#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
NP="${NP:-2}"

if [[ ! -d tmp/scf/si.save ]]; then
  echo "ERROR: run bash scripts/01_scf.sh first."
  exit 1
fi

mkdir -p outputs results/bands tmp
rm -rf tmp/bands
mkdir -p tmp/bands
cp -a tmp/scf/si.save tmp/bands/

echo "[BANDS] high-symmetry SeeK-path -> E_n(k)"
mpirun -np "$NP" pw.x -in inputs/si_bands.in > outputs/02_bands_pw.out

echo "[bands.x] convert/reformat band eigenvalues"
bands.x -in inputs/si_bands_pp.in > outputs/02_bands_x.out

echo "[projwfc.x] project each band state onto atomic s/p/... orbitals"
projwfc.x -in inputs/si_projwfc_bands.in > outputs/02_projwfc_bands.out

python scripts/plot_bands.py
python scripts/parse_projwfc_bands.py
python scripts/plot_projected_bands.py

echo
echo "Created:"
ls -1 results/bands
