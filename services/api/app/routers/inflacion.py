
from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from ..utils.inflacion import load_indices, save_indices

router = APIRouter(prefix="/inflacion", tags=["inflacion"])

@router.get("/indices")
async def get_indices():
    return load_indices()

class IndicesReq(BaseModel):
    base: str
    indices: Dict[str, float]

@router.post("/indices")
async def post_indices(req: IndicesReq):
    save_indices({"base": req.base, "indices": req.indices})
    return {"ok": True}
