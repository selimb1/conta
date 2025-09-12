
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
from ..config import settings
from ..utils.eecc_export import generate_eecc_zip

router = APIRouter(prefix="/eecc", tags=["eecc"])

class EECCParams(BaseModel):
    empresa: str
    fecha_corte: str
    comparativo: bool = True
    metodo_efe: str = "indirecto"  # "directo" | "indirecto" | "sintetico"

@router.post("/exportar")
async def exportar(params: EECCParams):
    out_zip = generate_eecc_zip(params.empresa, params.fecha_corte, params.comparativo, params.metodo_efe)
    rel = str(Path(out_zip).as_posix())
    return {"file": f"/files/{Path(out_zip).name}"}
