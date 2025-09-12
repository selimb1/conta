
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from ..utils.recpam_engine import reexpresar_moneda_cierre

router = APIRouter(prefix="/cierre", tags=["cierre"])

class Mov(BaseModel):
    fecha: str
    cuenta: str
    importe: float

class ReexpReq(BaseModel):
    fecha_cierre: str
    movimientos: List[Mov]

@router.post("/reexpresar")
async def reexpresar(req: ReexpReq):
    res = reexpresar_moneda_cierre([m.dict() for m in req.movimientos], req.fecha_cierre)
    # Asiento consolidado RECPAM: contra "Resultados financieros y por tenencia - RECPAM"
    asiento = {
        "fecha": req.fecha_cierre,
        "detalle": "RECPAM por reexpresión a moneda de cierre",
        "movimientos": []
    }
    total = res["recpam_total"]
    # Para demo: si RECPAM total > 0, se acredita resultado; si < 0, se debita
    if total != 0:
        if total > 0:
            asiento["movimientos"].append({"cuenta":"3.1. Resultados acumulados", "debe":0, "haber":0})  # placeholder PN si hiciera falta
            asiento["movimientos"].append({"cuenta":"5.9. RECPAM", "debe":0, "haber": total})
        else:
            asiento["movimientos"].append({"cuenta":"5.9. RECPAM", "debe": -total, "haber": 0})
            asiento["movimientos"].append({"cuenta":"3.1. Resultados acumulados", "debe":0, "haber":0})
    res["asiento_recpam"] = asiento
    return res
