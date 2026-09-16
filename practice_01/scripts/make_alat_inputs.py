from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]
template = (root / 'inputs' / 'si_diamond_scf_alat_TEMPLATE.in').read_text(encoding='utf-8')

out_dir = root / 'generated_inputs'
out_dir.mkdir(exist_ok=True)

with open(root / 'data' / 'assigned_alat.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        a_ang = float(row['alat_ang'])
        a_half = a_ang / 2.0

        text = template.replace('AHALF', f'{a_half:.10f}')
        filename = f'si_diamond_a_{a_ang:.4f}.in'
        (out_dir / filename).write_text(text, encoding='utf-8')

print(f'Wrote inputs to {out_dir}')
