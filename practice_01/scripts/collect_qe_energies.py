from pathlib import Path
import re
import csv

pattern = re.compile(r"!\\s+total energy\\s+=\\s+([-0-9.]+)\\s+Ry")
rows = []

for out in sorted(Path('.').glob('si_diamond_a_*.out')):
    text = out.read_text(errors='ignore')
    m = pattern.search(text)
    if not m:
        continue

    alat_ang = out.stem.replace('si_diamond_a_', '')
    rows.append((alat_ang, m.group(1), 'yes' if 'JOB DONE' in text else 'no'))

with open('ev_results.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['alat_ang', 'energy_Ry', 'job_done'])
    w.writerows(rows)

print(f'Collected {len(rows)} points into ev_results.csv')
