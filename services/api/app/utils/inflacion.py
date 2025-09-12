
from __future__ import annotations
from pathlib import Path
import json, datetime

IDX_FILE = Path(__file__).parent / "inflacion_indices.json"

def load_indices():
    if not IDX_FILE.exists():
        return {"base":"", "indices": {}}
    return json.loads(IDX_FILE.read_text(encoding="utf-8"))

def save_indices(data: dict):
    IDX_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def ym(d: str) -> str:
    # 'YYYY-MM-DD' -> 'YYYY-MM'
    return d[:7]

def coef(from_date: str, to_date: str) -> float:
    """Coeficiente RT 54: índice(to) / índice(from)"""
    data = load_indices()
    idx = data.get("indices", {})
    f, t = ym(from_date), ym(to_date)
    if f not in idx or t not in idx or idx[f] == 0:
        return 1.0
    return float(idx[t]) / float(idx[f])
