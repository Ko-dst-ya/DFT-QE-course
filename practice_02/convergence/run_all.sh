#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

bash ecut/run_ecut.sh
bash kgrid/run_kgrid.sh
python scripts/collect_convergence.py
python scripts/plot_convergence.py

echo "Results:"
echo "  convergence/ecut_convergence.csv"
echo "  convergence/kgrid_convergence.csv"
echo "  convergence/plots/*.png"
