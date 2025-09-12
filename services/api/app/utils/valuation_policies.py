
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path
import json, re

DEFAULT_POLICIES = [
  {"cuenta_regex": r"^1\.1\.1\.", "rubro":"Caja y Bancos", "inicial":"nominal", "posterior":"nominal", "ajuste_inflacion": True, "fx": "cierre"},
  {"cuenta_regex": r"^1\.1\.2\.", "rubro":"Inversiones temporarias", "inicial":"costo", "posterior":"fair_value|amortized_cost", "impairment":"vr<libro"},
  {"cuenta_regex": r"^(1\.1\.3\.|1\.2\.1\.)", "rubro":"Créditos", "inicial":"nominal(+CF)", "posterior":"amortized_cost", "incobrabilidad":"esperada", "impairment":"vr<libro"},
  {"cuenta_regex": r"^1\.1\.5\.", "rubro":"Bienes de cambio", "inicial":"costo", "posterior":"min(costo,VNR)"},
  {"cuenta_regex": r"^1\.2\.5\.", "rubro":"Bienes de uso", "inicial":"costo", "posterior":"costo|revaluacion", "depreciacion":"lineal", "impairment":"vr<libro"},
  {"cuenta_regex": r"^1\.2\.7\.", "rubro":"Intangibles", "inicial":"costo", "posterior":"costo", "amortizacion":"vida_util", "impairment":"vr<libro"},
  {"cuenta_regex": r"^2\.", "rubro":"Pasivos", "inicial":"costo", "posterior":"amortized_cost", "fx":"cierre"},
  {"cuenta_regex": r"^2\.9\.", "rubro":"Provisiones", "inicial":"mejor_estimacion", "posterior":"revaluar_cierre"},
  {"cuenta_regex": r"^3\.", "rubro":"Patrimonio Neto", "inicial":"nominal", "posterior":"moneda_cierre", "ajuste_inflacion": True}
]

POLICY_FILE = Path(__file__).parent / "valuation_policies.json"

def load_policies() -> List[Dict[str, Any]]:
    if POLICY_FILE.exists():
        return json.loads(POLICY_FILE.read_text(encoding="utf-8"))
    return DEFAULT_POLICIES

def save_policies(pols: List[Dict[str, Any]]) -> None:
    POLICY_FILE.write_text(json.dumps(pols, ensure_ascii=False, indent=2), encoding="utf-8")

def match_policy(codigo_cuenta: str, pols: List[Dict[str,Any]]):
    for p in pols:
        if re.search(p["cuenta_regex"], codigo_cuenta):
            return p
    return None
