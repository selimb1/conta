
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from ..utils.valuation_engine import valuar_y_reexpresar
from ..utils.valuation_policies import load_policies, save_policies

router = APIRouter(prefix="/cierre", tags=["cierre"])

class BalanceRow(BaseModel):
    cuenta: str
    desc: str = ""
    saldo_historico: float
    moneda: str = "ARS"
    fx: float | None = 1.0
    # opcionales por rubro
    vnr: float | None = None
    vida_util: float | None = None
    costo: float | None = None
    amort_acum: float | None = None
    perdida_esp: float | None = None

class ValuarReq(BaseModel):
    fecha_corte: str
    balances: List[BalanceRow]

@router.get("/politicas")
async def get_policies():
    return {"policies": load_policies()}

@router.post("/politicas")
async def set_policies(policies: List[Dict[str,Any]]):
    save_policies(policies); return {"ok": True}

@router.post("/valuar")
async def valuar(req: ValuarReq):
    res = valuar_y_reexpresar([r.dict() for r in req.balances], req.fecha_corte)
    return res
