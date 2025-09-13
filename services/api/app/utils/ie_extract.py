from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple

# Basic patterns
_re_cuit = re.compile(r"\b(\d{2})(\d{8})(\d)\b")
_re_cae  = re.compile(r"\bCAE[:\s-]*([0-9]{14})\b", re.IGNORECASE)
_re_fecha = re.compile(r"\b(\d{2})[/-](\d{2})[/-](\d{4})\b")
_re_total = re.compile(r"\bTOTAL(?:\s*FACTURA)?[:\s-]*\$?\s*([0-9\.,]+)\b", re.IGNORECASE)
_re_pv_nro = re.compile(r"\bPunto\s*de\s*Venta[:\s-]*0*(\d+)\b.*?\bComp(?:robante)?[:\s-]*0*(\d+)\b", re.IGNORECASE)
_re_tipo_afip = re.compile(
    r"\b(?:FACTURA|NOTA\s+DE\s+(?:DEBITO|DÉBITO|CREDITO|CRÉDITO))\s+([ABCM])\b",
    re.IGNORECASE,
)

def _norm_number(s: str) -> float | None:
    if not s: return None
    s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except: return None

def extract_fields(ocr_output: Dict[str, Any]) -> Dict[str, Any]:
    tokens: List[str] = ocr_output.get("tokens", [])
    full_text = " ".join(tokens)

    cuit_emisor = None
    m = _re_cuit.search(full_text)
    if m:
        cuit_emisor = "".join(m.groups())

    cae = None
    m = _re_cae.search(full_text)
    if m: cae = m.group(1)

    fecha = None
    m = _re_fecha.search(full_text)
    if m: fecha = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"

    total = None
    m = _re_total.search(full_text)
    if m: total = _norm_number(m.group(1))

    pv = numero = None
    m = _re_pv_nro.search(full_text)
    if m:
        pv = int(m.group(1))
        numero = int(m.group(2))

    tipo = None
    m = _re_tipo_afip.search(full_text)
    if m:
        tipo = m.group(1).upper()
    else:
        for i, tok in enumerate(tokens):
            up = tok.upper()
            if up in {"A", "B", "C", "M"}:
                context = " ".join(tokens[max(0, i - 2): i + 3]).upper()
                if "FACTURA" in context or "NOTA" in context:
                    tipo = up
                    break

    # crude VAT detection per common rates
    netos_por_alicuota = {}
    iva = {}
    for rate in (21, 10.5, 27):
        # Look for patterns like "IVA 21% $ 1234,56"
        r = re.compile(rf"\b(?:IVA)?\s*{rate}\s*%[:\s-]*\$?\s*([0-9\.,]+)\b")
        mm = r.search(full_text)
        if mm:
            iva_val = _norm_number(mm.group(1)) or 0.0
            iva[str(rate)] = iva_val

    campos = {
        "cuit_emisor": cuit_emisor,
        "tipo": tipo,
        "pv": pv,
        "numero": numero,
        "fecha": fecha,
        "moneda": "ARS",
        "netos_por_alicuota": netos_por_alicuota,  # Completar si se detectan netos
        "iva": iva,
        "exento": 0.0,
        "no_gravado": 0.0,
        "percepciones": {},
        "total": total,
        "cae": cae,
        "qr_hash": None,
    }
    return campos