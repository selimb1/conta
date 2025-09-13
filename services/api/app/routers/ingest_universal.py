from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Depends
from pathlib import Path
from sqlalchemy.orm import Session
from ..config import settings
from ..db import get_db
from ..models import Documento
from ..utils.universal_pipeline import procesar_universal
from ..utils.validators import validate_fields
from ..utils.accounting_rules import propose_entry
from ..utils.exporters import export_outputs

router = APIRouter(prefix="/ingesta", tags=["ingesta"])

@router.post("/procesar_universal")
async def procesar_universal(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    target = Path(settings.STORAGE_DIR) / file.filename
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as f:
        f.write(await file.read())

    doc = Documento(tipo=file.content_type or "desconocido", ruta_archivo=str(target))
    db.add(doc)
    db.commit()
    db.refresh(doc)
    doc_id = str(doc.id)

    result = procesar_universal(target)
    vals = validate_fields(result["campos_extraidos"])
    asiento = propose_entry(result["campos_extraidos"])
    exports = export_outputs(doc_id)

    out = {
        "documento_id": doc_id,
        "validaciones": vals,
        "campos_extraidos": result["campos_extraidos"],
        "asiento_propuesto": asiento,
        "alertas": [],
        "libros_y_ddjj_preliminares": {"iva": {}, "ganancias": {}, "iibb": {}},
        "archivos_exportables": exports["files"],
        "items": result["items"],
        "pages": result["pages"],
    }
    return out