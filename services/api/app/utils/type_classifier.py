from __future__ import annotations
import re
from typing import Optional, Dict

AFIP_TIPO_MAP = {
    1: ("A", "Factura"), 2: ("A", "Nota de Débito"), 3: ("A", "Nota de Crédito"),
    6: ("B", "Factura"), 7: ("B", "Nota de Débito"), 8: ("B", "Nota de Crédito"),
    11: ("C", "Factura"), 12: ("C", "Nota de Débito"), 13: ("C", "Nota de Crédito"),
    51: ("M", "Factura"), 52: ("M", "Nota de Débito"), 53: ("M", "Nota de Crédito"),
}

def classify_from_text(text: str) -> Dict[str, Optional[str]]:
    t = text.upper()
    m = re.search(r"\b(NOTA\s+DE\s+(CREDITO|CRÉDITO|DEBITO|DÉBITO)|FACTURA)\s+([ABCM])\b", t)
    doc = None; letra = None
    if m:
        doc = "Nota de " + (m.group(2).capitalize() if m.group(1).startswith("NOTA") else "") if m.group(1).startswith("NOTA") else "Factura"
        if "FACTURA" in m.group(0): doc = "Factura"
        if "CREDITO" in m.group(0) or "CRÉDITO" in m.group(0): doc = "Nota de Crédito"
        if "DEBITO" in m.group(0) or "DÉBITO" in m.group(0): doc = "Nota de Débito"
        letra = m.group(3)
    else:
        if "FACTURA" in t: doc = "Factura"
        if "NOTA DE CREDITO" in t or "NOTA DE CRÉDITO" in t: doc = "Nota de Crédito"
        if "NOTA DE DEBITO" in t or "NOTA DE DÉBITO" in t: doc = "Nota de Débito"
        m2 = re.search(r"FACTURA\s+([ABCM])\b", t)
        if m2: letra = m2.group(1)
    return {"tipo_doc": doc, "letra": letra}

def from_afip_tipo(tipo_cmp: int) -> Dict[str, Optional[str]]:
    letter, nature = AFIP_TIPO_MAP.get(int(tipo_cmp), (None, None))
    return {"tipo_doc": nature, "letra": letter}