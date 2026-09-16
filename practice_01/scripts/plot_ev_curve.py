import csv
import matplotlib.pyplot as plt

volume = []
energy = []

with open('ev_results.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        a_ang = float(row['alat_ang'])
        e_ry = float(row['energy_Ry'])

        volume_per_atom = a_ang**3 / 8.0
        energy_per_atom = e_ry / 2.0

        volume.append(volume_per_atom)
        energy.append(energy_per_atom)

plt.figure()
plt.plot(volume, energy, marker='o')
plt.xlabel(r'$V$ per atom ($\\AA^3$)')
plt.ylabel('Energy per atom (Ry)')
plt.tight_layout()
plt.savefig('ev_curve.png', dpi=200)

print('Saved ev_curve.png')
