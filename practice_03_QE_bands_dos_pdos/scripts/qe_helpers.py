from pathlib import Path
import re

def read_vbm(scf_out: Path) -> float:
    text = scf_out.read_text(errors="ignore")
    matches = re.findall(r"highest occupied level\s*\(ev\):\s*([-+0-9.Ee]+)", text, flags=re.I)
    if matches:
        return float(matches[-1])
    matches = re.findall(
        r"highest occupied,\s*lowest unoccupied level\s*\(ev\):\s*([-+0-9.Ee]+)\s+([-+0-9.Ee]+)",
        text, flags=re.I
    )
    if matches:
        return float(matches[-1][0])
    raise RuntimeError("Could not find VBM in SCF output.")

def pretty_label(label: str) -> str:
    return "Γ" if label == "GAMMA" else label.replace("_", "₋")
