from __future__ import annotations
from typing import List, Dict, Any

def tables_to_items(tables: List[List[List[str]]]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not tables: return items
    for table in tables:
        if not table or len(table) < 2: continue
        headers = [ (h or "").strip().lower() for h in table[0] ]
        def find_col(keys): 
            for i, h in enumerate(headers):
                if any(k in h for k in keys): return i
            return None
        c_desc = find_col(["desc", "detalle", "concepto"])
        c_cant = find_col(["cant", "cantidad"])
        c_pu   = find_col(["unit", "u.", "precio"])
        c_alic = find_col(["alícuota", "alicuota", "% iva"])
        c_neto = find_col(["neto"])
        c_iva  = find_col(["iva"])
        c_tot  = find_col(["total"])

        for row in table[1:]:
            def val(idx): 
                try: return (row[idx] or "").strip()
                except: return ""
            item = {
                "descripcion": val(c_desc) if c_desc is not None else "",
                "cantidad": _to_num(val(c_cant)) if c_cant is not None else None,
                "p_unitario": _to_num(val(c_pu)) if c_pu is not None else None,
                "alicuota_iva": _to_num(val(c_alic)) if c_alic is not None else None,
                "neto": _to_num(val(c_neto)) if c_neto is not None else None,
                "iva": _to_num(val(c_iva)) if c_iva is not None else None,
                "total": _to_num(val(c_tot)) if c_tot is not None else None,
            }
            if any([item["descripcion"], item["cantidad"], item["neto"], item["iva"], item["total"]]):
                items.append(item)
    return items

def _to_num(s: str):
    if not s: return None
    s = s.replace(".", "").replace(",", ".")
    try: return float(s)
    except: return None