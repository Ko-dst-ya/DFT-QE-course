# Folding extension: 2-atom vs 8-atom Si

This folder contains `structure/si_conventional_8atoms.cif` in the parent
practice package for a later band-folding demonstration.

Core practice uses the **2-atom standardized primitive cell**.

Recommended lecture sequence for folding:
1. show ARPES/experimental-like Si valence-band dispersion from Giustino;
2. show calculated bands for the 2-atom primitive cell;
3. show the same valence-band physics represented in an 8-atom conventional/supercell cell;
4. explain: a larger real-space cell has a smaller reciprocal cell, so states are folded
   into more bands.

This extension is intentionally NOT part of `run_all.sh`: first test the core
SCF -> bands -> DOS/PDOS workflow. Then choose the exact reciprocal path for
the 8-atom representation so the comparison answers the pedagogical question
you want to show.
