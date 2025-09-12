
from __future__ import annotations
from pathlib import Path
import csv, zipfile, datetime
from typing import List

from .exporters import ensure_exports_dir
from .eecc_templates import write_csv_templates, write_docx_templates

def generate_eecc_zip(empresa: str, fecha_corte: str, comparativo: bool, metodo_efe: str) -> str:
    exports = ensure_exports_dir()
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = exports / f"EECC_{empresa}_{fecha_corte}_{stamp}"
    folder.mkdir(parents=True, exist_ok=True)

    saldos = None
    salfile = exports / "last_saldos_valuados.json"
    if salfile.exists():
        import json
        saldos = json.loads(salfile.read_text(encoding="utf-8"))
    

    write_csv_templates(folder, empresa, fecha_corte, comparativo, metodo_efe, saldos)
    write_docx_templates(folder, empresa, fecha_corte, comparativo, metodo_efe)

    zip_path = exports / f"EECC_{empresa}_{fecha_corte}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in folder.iterdir():
            z.write(f, arcname=f.name)
    return str(zip_path)
