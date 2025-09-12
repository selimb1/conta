from __future__ import annotations
from fastapi import APIRouter
from typing import Dict, Any
from ..utils.exporters import export_eeff_xlsx, export_libro_iva

router = APIRouter(prefix="/eeff", tags=["eeff"])

@router.post("/export")
def export_eeff(empresa: str, fecha_corte: str, esp: Dict[str, Any], eerr: Dict[str, Any], eepn: Dict[str, Any]):
    path = export_eeff_xlsx(empresa, fecha_corte, esp, eerr, eepn)
    return {"file": path}

@router.post("/libro-iva")
def export_libro(empresa: str, periodo: str, compras: list[dict], ventas: list[dict]):
    path = export_libro_iva(empresa, periodo, compras, ventas)
    return {"file": path}