from __future__ import annotations
from typing import Dict, Any, List
from pathlib import Path
import mimetypes

from .pdf_native import extract_pdf_native
from .ocr_pipeline import run_ocr
from .ie_extract import extract_fields as extract_fields_from_tokens
from .table_items import tables_to_items
from .qr_afip import parse_afip_qr_payload
from .type_classifier import classify_from_text, from_afip_tipo

def is_pdf(path: Path) -> bool:
    typ, _ = mimetypes.guess_type(path.name)
    return (typ == "application/pdf") or path.suffix.lower() == ".pdf"

def procesar_universal(path: Path) -> Dict[str, Any]:
    pages: List[Dict[str, Any]] = []
    items: List[Dict[str, Any]] = []

    if is_pdf(path):
        pdf = extract_pdf_native(path)
        pages = pdf["pages"]
        for p in pages:
            items.extend(tables_to_items(p.get("tables", [])))
        full_text = " ".join(p.get("text","") or "" for p in pages)
        campos = _extract_campos_from_text(full_text)
    else:
        ocr = run_ocr(path)
        pages = [{
            "text": " ".join(ocr.get("tokens", [])),
            "blocks": [], "tables": [],
            "ocr_tokens": ocr.get("tokens", []),
            "ocr_bboxes": ocr.get("bboxes", []),
            "ocr_confs": ocr.get("confs", [])
        }]
        campos = extract_fields_from_tokens(ocr)

    qr_found = _find_afip_qr_in_pages(pages)
    if qr_found:
        qr = parse_afip_qr_payload(qr_found)
        if qr:
            campos = _merge_campos_with_qr(campos, qr)
            if qr.get("tipo_cod"):
                tipo = from_afip_tipo(qr["tipo_cod"])
                campos["tipo_doc"] = campos.get("tipo_doc") or tipo["tipo_doc"]
                campos["letra"] = campos.get("letra") or tipo["letra"]

    if not campos.get("tipo_doc") or not campos.get("letra"):
        t_all = " ".join(p.get("text","") or "" for p in pages)
        guess = classify_from_text(t_all)
        campos["tipo_doc"] = campos.get("tipo_doc") or guess["tipo_doc"]
        campos["letra"] = campos.get("letra") or guess["letra"]

    return {
        "campos_extraidos": campos,
        "pages": pages,
        "items": items,
        "validaciones": []
    }

def _find_afip_qr_in_pages(pages: List[Dict[str,Any]]) -> str | None:
    import re
    pat = re.compile(r"https?://(?:www\.)?afip\.gov\.ar/fe/qr/\?p=[A-Za-z0-9_=+-/]+", re.IGNORECASE)
    for p in pages:
        txt = p.get("text") or ""
        m = pat.search(txt)
        if m:
            return m.group(0)
    return None

def _merge_campos_with_qr(campos: Dict[str,Any], qr: Dict[str,Any]) -> Dict[str,Any]:
    out = dict(campos)
    for k_map, qk in [("cuit_emisor","cuit_emisor"), ("pv","pv"), ("numero","numero"), ("cae","cae"), ("total","total"), ("moneda","moneda")]:
        if not out.get(k_map) and qr.get(qk) is not None:
            out[k_map] = qr[qk]
    if not out.get("fecha") and qr.get("fecha"):
        out["fecha"] = qr["fecha"]
    return out

def _extract_campos_from_text(full_text: str) -> Dict[str,Any]:
    ocr_stub = {"tokens": full_text.split()}
    from .ie_extract import extract_fields
    return extract_fields(ocr_stub)