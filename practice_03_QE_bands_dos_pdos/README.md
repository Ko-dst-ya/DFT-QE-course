# Practice 3 — Si bands, DOS, PDOS and projected bands (Quantum ESPRESSO)

## The one picture to remember: three k-point tasks

```text
                       one relaxed structure
                              |
              +---------------+---------------+
              |               |               |
        uniform mesh     high-sym path    dense uniform mesh
          (6x6x6)         (SeeK-path)         (12x12x12)
              |               |               |
             SCF            bands            NSCF
              |               |               |
       self-consistent     E_n(k)          many eigenvalues
          density            |               |
                              |          dos.x -> DOS
                         projwfc.x       projwfc.x -> PDOS
                              |
                      projected / fat bands
```

**Do not mix these roles.**
- SCF mesh: Brillouin-zone integration and self-consistent density.
- Band path: visualize the dispersion `E_n(k)`.
- Dense uniform mesh: integrate DOS/PDOS accurately enough.

## 0. Requirements

```bash
python -c "import numpy, matplotlib, pymatgen, seekpath; print('OK')"
pw.x -h
bands.x -h
dos.x -h
projwfc.x -h
```

For Materials Project (optional in the core run):

```bash
python -c "import mp_api; print('mp-api OK')"
```

## 1. Prepare SeeK-path and QE inputs

The package already contains a relaxed 2-atom Si CIF.

On the course VM:

```bash
export QE_PSEUDO_DIR=/home/md/Software/qe-7.5/pseudo
export QE_PSEUDO_FILE=Si_r.upf
bash scripts/00_prepare.sh
```

On Linux/macOS with another installation, change only the environment variables.

What `00_prepare.sh` does:
1. reads `structure/si_relaxed_primitive.cif`;
2. calls **SeeK-path**;
3. gets the standardized primitive cell;
4. writes the explicit high-symmetry path;
5. creates all QE `.in` files consistently for that standardized cell.

Inspect:

```bash
cat generated/seekpath_summary.txt
vesta generated/si_seekpath_primitive.cif
less inputs/si_scf.in
less inputs/si_bands.in
less inputs/si_nscf_dos.in
```

### What changes between the three pw.x inputs?

| Input | k points | Property/task |
|---|---|---|
| `si_scf.in` | uniform 6x6x6 | self-consistent density and total energy |
| `si_bands.in` | explicit SeeK-path | band energies along a high-symmetry path |
| `si_nscf_dos.in` | dense uniform 12x12x12 | eigenvalues for DOS/PDOS integration |

The structure, pseudopotential and cutoffs are kept consistent.

---

## 2. Branch 1 — SCF

```bash
bash scripts/01_scf.sh
```

Inside the script the key command is:

```bash
mpirun -np 2 pw.x -in inputs/si_scf.in > outputs/01_scf.out
```

What we obtain:
- converged charge density;
- total energy;
- VBM / highest occupied level;
- a `si.save` directory needed by the two later branches.

Inspect:

```bash
grep "!" outputs/01_scf.out
grep -i "highest occupied" outputs/01_scf.out
grep "JOB DONE" outputs/01_scf.out
```

---

## 3. Branch 2 — band structure and orbital character

```bash
bash scripts/02_bands.sh
```

It performs three physical/post-processing steps.

### 3.1 `pw.x`, calculation = 'bands'

Reads the SCF density but diagonalizes the Kohn-Sham Hamiltonian only at the
explicit k-points supplied by SeeK-path.

Property:

```text
E_n(k) along a high-symmetry path
```

### 3.2 `bands.x`

```bash
bands.x -in inputs/si_bands_pp.in
```

`bands.x` reformats the eigenvalues and writes

```text
results/bands/si_bands.dat.gnu
```

for plotting.

### 3.3 `projwfc.x` on the band path

```bash
projwfc.x -in inputs/si_projwfc_bands.in
```

This projects each Kohn-Sham state onto pseudo-atomic orbitals from the
pseudopotential. The supplied Python parser groups the weights by angular
momentum:

```text
l = 0 -> s
l = 1 -> p
```

Outputs:

```text
results/bands/si_bands.png
results/bands/si_bands_s_projected.png
results/bands/si_bands_p_projected.png
results/bands/si_projected_bands.csv
```

Interpretation:
- **PDOS** answers which orbital characters occur near a given energy.
- **projected bands** answer which orbital character a particular band
  `n,k` has.

---

## 4. Branch 3 — DOS and PDOS

```bash
bash scripts/03_dos_pdos.sh
```

### 4.1 Dense uniform NSCF

```text
calculation = 'nscf'
K_POINTS automatic
12 12 12 1 1 1
```

The charge density is not rebuilt self-consistently. We sample many k-points
using the already converged SCF potential.

### 4.2 `dos.x`

```bash
dos.x -in inputs/si_dos_pp.in
```

Property:

```text
DOS(E): number of electronic states per energy interval
```

### 4.3 `projwfc.x`

```bash
projwfc.x -in inputs/si_projwfc_dos.in
```

Property:

```text
PDOS(E): DOS resolved by atomic pseudo-orbital character
```

For Si the supplied plot sums the two atoms and compares total DOS with the
Si `s` and `p` contributions:

```text
results/dos/si_DOS_PDOS_sp.png
```

---

## 5. Run everything

After you understand the separate steps:

```bash
bash scripts/run_all.sh
```

Do **not** treat `run_all.sh` as a black box. Read it:

```bash
cat scripts/run_all.sh
```

The point of the shell scripts is to remove typing errors, not to hide the workflow.

---

## 6. Optional: fetch Si from Materials Project

After setting your MP API key:

```bash
python scripts/fetch_mp149.py
```

This creates:

```text
structure/mp-149_from_MP.cif
```

You can then run the SeeK-path preparation script on that CIF instead of the
bundled relaxed structure.

---

## 7. Folding

The core workflow uses the 2-atom primitive cell.

For the lecture/demo, `structure/si_conventional_8atoms.cif` is included.
The suggested comparison is:

```text
ARPES / reference Si valence bands
        ->
2-atom primitive-cell bands
        ->
8-atom-cell folded representation
```

The automated 8-atom band path is deliberately not in `run_all.sh` yet.
Choose it only after deciding exactly which reciprocal-space comparison you
want to show.
