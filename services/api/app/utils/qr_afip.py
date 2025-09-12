from __future__ import annotations
import base64, json, re
from typing import Dict, Any, Optional

AFIP_QR_REGEX = re.compile(r"https?://(www\.)?afip\.gov\.ar/fe/qr/\?p=([A-Za-z0-9_=+-/]+)", re.IGNORECASE)

def parse_afip_qr_payload(qr_text_or_url: str) -> Optional[Dict[str, Any]]:
    """
    Acepta la URL completa del QR o el contenido base64; devuelve dict con los campos normalizados.
    Estructura típica (ejemplo):
    {
      'ver': 1,
      'fecha': '2025-08-30',
      'cuit': 30709999999,
      'ptoVta': 1,
      'tipoCmp': 1,
      'nroCmp': 1234,
      'importe': 121000.0,
      'moneda': 'PES',
      'ctz': 1,
      'tipoDocRec': 80,
      'nroDocRec': 20300123456,
      'tipoCodAut': 'E',
      'codAut': 73123456789012
    }
    """
    m = AFIP_QR_REGEX.search(qr_text_or_url or "")
    payload_b64 = None
    if m:
        payload_b64 = m.group(2)
    else:
        s = (qr_text_or_url or "").strip()
        if s and all(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=" for c in s):
            payload_b64 = s
    if not payload_b64:
        return None
    try:
        raw = base64.b64decode(payload_b64 + "===")
        data = json.loads(raw.decode("utf-8", errors="ignore"))
        out = {
            "ver": data.get("ver"),
            "fecha": data.get("fecha"),
            "cuit_emisor": str(data.get("cuit") or ""),
            "pv": data.get("ptoVta"),
            "tipo_cod": data.get("tipoCmp"),
            "numero": data.get("nroCmp"),
            "total": float(data.get("importe") or 0),
            "moneda": data.get("moneda"),
            "ctz": data.get("ctz"),
            "tipo_doc_rec": data.get("tipoDocRec"),
            "doc_receptor": str(data.get("nroDocRec") or ""),
            "tipoCodAut": data.get("tipoCodAut"),
            "cae": str(data.get("codAut") or ""),
        }
        return out
    except Exception:
        return None