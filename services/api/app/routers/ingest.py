from fastapi import APIRouter, UploadFile, File, Depends
from pathlib import Path
from sqlalchemy.orm import Session
from ..config import settings
from ..db import get_db
from ..models import Documento
from ..schemas import ProcesamientoOut
from ..utils.ocr_pipeline import run_ocr
from ..utils.ie_extract import extract_fields
from ..utils.validators import validate_fields
from ..utils.accounting_rules import propose_entry
from ..utils.exporters import export_outputs

router = APIRouter(prefix="/ingesta", tags=["ingesta"])

@router.post("/procesar", response_model=ProcesamientoOut)
async def procesar(
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

    ocr = run_ocr(target)
    campos = extract_fields(ocr)
    vals = validate_fields(campos)
    asiento = propose_entry(campos)
    exports = export_outputs(doc_id)

    return {
        "documento_id": doc_id,
        "validaciones": vals,
        "campos_extraidos": campos,
        "asiento_propuesto": asiento,
        "alertas": [],
        "libros_y_ddjj_preliminares": {"iva": {}, "ganancias": {}, "iibb": {}},
        "archivos_exportables": exports["files"],
    }