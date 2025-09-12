from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import Empresa
from ..utils.validators import validar_cuit

router = APIRouter(prefix="/clientes", tags=["clientes"])

class ClienteIn(BaseModel):
    razon_social: str = Field(..., min_length=2)
    cuit: str = Field(..., min_length=11, max_length=13)
    condicion_iva: str = Field(..., description="RI | Exento | Monotributo")

class ClienteOut(ClienteIn):
    id: str

@router.get("", response_model=list[ClienteOut])
def list_clientes(q: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Empresa)
    if q:
        qlike = f"%{q}%"
        query = query.filter((Empresa.razon_social.ilike(qlike)) | (Empresa.cuit.ilike(qlike)))
    rows = query.order_by(Empresa.razon_social.asc()).limit(200).all()
    return [ClienteOut(id=str(r.id), razon_social=r.razon_social, cuit=r.cuit, condicion_iva=r.condicion_iva) for r in rows]

@router.post("", response_model=ClienteOut)
def create_cliente(payload: ClienteIn, db: Session = Depends(get_db)):
    if not validar_cuit(payload.cuit):
        raise HTTPException(422, "CUIT inválido")
    exists = db.query(Empresa).filter(Empresa.cuit == payload.cuit).first()
    if exists:
        raise HTTPException(409, "Ya existe una empresa con ese CUIT")
    e = Empresa(razon_social=payload.razon_social.strip(), cuit=payload.cuit.strip(), condicion_iva=payload.condicion_iva.strip())
    db.add(e); db.commit(); db.refresh(e)
    return ClienteOut(id=str(e.id), razon_social=e.razon_social, cuit=e.cuit, condicion_iva=e.condicion_iva)

@router.put("/{empresa_id}", response_model=ClienteOut)
def update_cliente(empresa_id: str, payload: ClienteIn, db: Session = Depends(get_db)):
    if not validar_cuit(payload.cuit):
        raise HTTPException(422, "CUIT inválido")
    e = db.query(Empresa).get(empresa_id)
    if not e:
        raise HTTPException(404, "Cliente no encontrado")
    e.razon_social = payload.razon_social.strip()
    e.cuit = payload.cuit.strip()
    e.condicion_iva = payload.condicion_iva.strip()
    db.commit(); db.refresh(e)
    return ClienteOut(id=str(e.id), razon_social=e.razon_social, cuit=e.cuit, condicion_iva=e.condicion_iva)

@router.delete("/{empresa_id}")
def delete_cliente(empresa_id: str, db: Session = Depends(get_db)):
    e = db.query(Empresa).get(empresa_id)
    if not e:
        raise HTTPException(404, "Cliente no encontrado")
    db.delete(e); db.commit()
    return {"ok": True}
