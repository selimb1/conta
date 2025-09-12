from __future__ import annotations
from typing import Dict, List
from pathlib import Path
import datetime as dt
import xlsxwriter

EXPORT_DIR = Path("./exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def _wb(path: Path):
    return xlsxwriter.Workbook(str(path))

def export_libro_iva(empresa: str, periodo: str, compras: List[Dict], ventas: List[Dict]) -> str:
    path = EXPORT_DIR / f"libro_iva_{empresa}_{periodo}.xlsx"
    wb = _wb(path)
    fmt_hdr = wb.add_format({"bold": True, "bg_color": "#EEEEEE"})
    # Compras
    sh = wb.add_worksheet("Compras")
    headers = ["Fecha","Tipo","PV","Nro","CUIT Emisor","Neto 21","Neto 10.5","Neto 27","IVA 21","IVA 10.5","IVA 27","Exento","No Gravado","Percep IVA","Percep IIBB","Total"]
    for c,h in enumerate(headers): sh.write(0,c,h,fmt_hdr)
    for r,row in enumerate(compras, start=1):
        for c,val in enumerate([row.get(k) for k in ["fecha","tipo","pv","numero","cuit_emisor","neto_21","neto_10_5","neto_27","iva_21","iva_10_5","iva_27","exento","no_gravado","percep_iva","percep_iibb","total"]]):
            sh.write(r,c,val)
    # Ventas
    sh = wb.add_worksheet("Ventas")
    for c,h in enumerate(headers): sh.write(0,c,h,fmt_hdr)
    for r,row in enumerate(ventas, start=1):
        for c,val in enumerate([row.get(k) for k in ["fecha","tipo","pv","numero","cuit_receptor","neto_21","neto_10_5","neto_27","iva_21","iva_10_5","iva_27","exento","no_gravado","percep_iva","percep_iibb","total"]]):
            sh.write(r,c,val)
    wb.close()
    return str(path)

def export_eeff_xlsx(empresa: str, fecha_corte: str, esp: Dict, eerr: Dict, eepn: Dict) -> str:
    path = EXPORT_DIR / f"eeff_{empresa}_{fecha_corte}.xlsx"
    wb = _wb(path)
    fmt_hdr = wb.add_format({"bold": True, "bg_color": "#EEEEEE"})
    # ESP
    sh = wb.add_worksheet("ESP")
    sh.write_row(0,0,["Rubros","Importe"], fmt_hdr)
    for i,(k,v) in enumerate([
        ("Activo Corriente", esp.get("activo_corriente",0)),
        ("Activo No Corriente", esp.get("activo_no_corriente",0)),
        ("Pasivo Corriente", esp.get("pasivo_corriente",0)),
        ("Pasivo No Corriente", esp.get("pasivo_no_corriente",0)),
        ("Patrimonio Neto", esp.get("patrimonio_neto",0)),
    ], start=1):
        sh.write(i,0,k); sh.write(i,1,v)
    # EERR
    sh = wb.add_worksheet("EERR")
    sh.write_row(0,0,["Concepto","Importe"], fmt_hdr)
    for i,(k,v) in enumerate([
        ("Ventas Netas", eerr.get("ventas",0)),
        ("Costo de Ventas", eerr.get("costo_ventas",0)),
        ("Gastos Com", eerr.get("gastos_com",0)),
        ("Gastos Adm", eerr.get("gastos_adm",0)),
        ("Resultados Fin", eerr.get("res_fin",0)),
        ("Otros", eerr.get("otros",0)),
        ("Impuesto a las Ganancias", eerr.get("imp_gan",0)),
        ("Resultado Neto", eerr.get("resultado_neto",0)),
    ], start=1):
        sh.write(i,0,k); sh.write(i,1,v)
    # EEPN
    sh = wb.add_worksheet("EEPN")
    sh.write_row(0,0,["Columna","Importe"], fmt_hdr)
    for i,(k,v) in enumerate(eepn.items(), start=1):
        sh.write(i,0,k); sh.write(i,1,v)
    wb.close()
    return str(path)

def export_outputs(doc_id: str) -> Dict:
    # Minimal placeholder keeps previous behavior
    return {"files": ["eeff.xlsx", "libro_iva.xlsx"]}