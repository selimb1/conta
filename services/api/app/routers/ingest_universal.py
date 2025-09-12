from __future__ import annotations
from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from ..config import settings
from ..utils.universal_pipeline import procesar_universal
from ..utils.validators import validate_fields
from ..utils.accounting_rules import propose_entry
from ..utils.exporters import export_outputs

router = APIRouter(prefix="/ingesta", tags=["ingesta"])

@router.post("/procesar_universal")
async def procesar_universal(file: UploadFile = File(...)):
    target = Path(settings.STORAGE_DIR) / file.filename
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as f:
        f.write(await file.read())

    result = procesar_universal(target)
    vals = validate_fields(result["campos_extraidos"])
    asiento = propose_entry(result["campos_extraidos"])
    exports = export_outputs("doc-id-placeholder")

    out = {
        "validaciones": vals,
        "campos_extraidos": result["campos_extraidos"],
        "asiento_propuesto": asiento,
        "alertas": [],
        "libros_y_ddjj_preliminares": {"iva": {}, "ganancias": {}, "iibb": {}},
        "archivos_exportables": exports["files"],
        "items": result["items"],
        "pages": result["pages"]
    }
    return out