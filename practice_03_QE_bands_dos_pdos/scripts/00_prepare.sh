#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PSEUDO_DIR="${QE_PSEUDO_DIR:-/home/md/Software/qe-7.5/pseudo}"
PSEUDO_FILE="${QE_PSEUDO_FILE:-Si_r.upf}"

echo "QE_PSEUDO_DIR = $PSEUDO_DIR"
echo "QE_PSEUDO_FILE = $PSEUDO_FILE"

if [[ ! -f "$PSEUDO_DIR/$PSEUDO_FILE" ]]; then
  echo "ERROR: pseudopotential not found: $PSEUDO_DIR/$PSEUDO_FILE"
  echo "Set it, for example:"
  echo "  export QE_PSEUDO_DIR=/your/path/to/pseudo"
  echo "  export QE_PSEUDO_FILE=Si_r.upf"
  exit 1
fi

python scripts/00_prepare_si_seekpath.py \
  structure/si_relaxed_primitive.cif \
  --pseudo-dir "$PSEUDO_DIR" \
  --pseudo-file "$PSEUDO_FILE"

echo
echo "SeeK-path summary:"
cat generated/seekpath_summary.txt
