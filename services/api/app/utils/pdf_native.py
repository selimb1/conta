from __future__ import annotations
from typing import List, Dict, Any, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import pdfplumber

def extract_pdf_native(path: Path) -> Dict[str, Any]:
    out_pages: List[Dict[str, Any]] = []
    with fitz.open(str(path)) as doc:
        for page in doc:
            blocks = page.get_text("blocks")
            page_text = page.get_text()
            b_out = [{"text": b[4], "bbox": [b[0], b[1], b[2], b[3]]} for b in blocks if len(b) >= 5]
            out_pages.append({"text": page_text, "blocks": b_out, "tables": []})

    try:
        with pdfplumber.open(str(path)) as pdf:
            for i, p in enumerate(pdf.pages):
                try:
                    tables = p.extract_tables()
                except Exception:
                    tables = []
                out_pages[i]["tables"] = tables or []
    except Exception:
        pass

    return {"pages": out_pages}