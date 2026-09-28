#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

bash scripts/00_prepare.sh
bash scripts/01_scf.sh
bash scripts/02_bands.sh
bash scripts/03_dos_pdos.sh

echo
echo "Practice 3 workflow finished."
echo "Open:"
echo "  results/bands/si_bands.png"
echo "  results/bands/si_bands_s_projected.png"
echo "  results/bands/si_bands_p_projected.png"
echo "  results/dos/si_DOS_PDOS_sp.png"
