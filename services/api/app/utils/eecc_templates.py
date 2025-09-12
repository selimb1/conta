
from __future__ import annotations
from pathlib import Path
import csv
from typing import List
import datetime
import zipfile

def _hdr(entity: str, fecha: str):
    return [f"Denominación: {entity}", f"Fecha: {fecha}", "Moneda homogénea", "Comparativo Actual/Anterior"]

def write_csv_templates(folder: Path, empresa: str, fecha: str, comparativo: bool, metodo_efe: str, saldos: list|None=None):
    # ESP
    with (folder / "ESP.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(_hdr(empresa, fecha))
        w.writerow(["ESTADO DE SITUACIÓN PATRIMONIAL (RT 9)"])
        w.writerow(["Rubro","Actual","Anterior","","Rubro","Actual","Anterior"]); sal_map = {}
        # Activo
        activos = ["Activo corriente","Caja y bancos","Inversiones temporarias","Créditos por ventas","Otros créditos","Bienes de cambio","Otros activos","Total activo corriente",
                   "Activo no corriente","Créditos por ventas","Otros créditos","Bienes de cambio","Bienes de uso","Participaciones en sociedades","Otras inversiones","Activos intangibles","Otros activos","Total activo no corriente","TOTAL ACTIVO"]
        pasivos = ["Pasivo corriente","Deudas comerciales","Préstamos","Remuneraciones y cargas sociales","Cargas fiscales","Anticipos de clientes","Dividendos a pagar","Otras deudas","Total pasivo corriente",
                   "Pasivo no corriente","Deudas","Total deudas","Previsiones","Total pasivo no corriente","TOTAL PASIVO","PATRIMONIO NETO (según EEPN)","TOTAL PASIVO Y PN"]
        
        # Si vienen saldos valuados, volcamos en la sección correspondiente (simplificado)
        if saldos:
            for s in saldos:
                rub = s.get("rubro","Otros"); cta = s.get("cuenta",""); val = s.get("saldo_valuado",0)
                sal_map.setdefault(rub, []).append((cta, val))
            # Caja y bancos
            if "Caja y Bancos" in sal_map:
                for cta,val in sal_map["Caja y Bancos"]:
                    w.writerow([f"  {cta}", f"{val:.2f}", "", "", "", "", ""])
            # Créditos
            if "Créditos" in sal_map:
                for cta,val in sal_map["Créditos"]:
                    w.writerow([f"  {cta}", f"{val:.2f}", "", "", "", "", ""])
            # Bienes de cambio
            if "Bienes de cambio" in sal_map:
                for cta,val in sal_map["Bienes de cambio"]:
                    w.writerow([f"  {cta}", f"{val:.2f}", "", "", "", "", ""])
            # Bienes de uso
            if "Bienes de uso" in sal_map:
                for cta,val in sal_map["Bienes de uso"]:
                    w.writerow([f"  {cta}", f"{val:.2f}", "", "", "", "", ""])
            # Intangibles
            if "Intangibles" in sal_map:
                for cta,val in sal_map["Intangibles"]:
                    w.writerow([f"  {cta}", f"{val:.2f}", "", "", "", "", ""])
            # Pasivos
            if "Pasivos" in sal_map:
                for cta,val in sal_map["Pasivos"]:
                    w.writerow(["", "", "", "", f"  {cta}", f"{abs(val):.2f}", ""])
    
        for i in range(max(len(activos), len(pasivos))):
            a = activos[i] if i < len(activos) else ""
            p = pasivos[i] if i < len(pasivos) else ""
            w.writerow([a,"","", "", p,"",""])

    # EERR
    with (folder / "EERR.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(_hdr(empresa, fecha))
        w.writerow(["ESTADO DE RESULTADOS (RT 9)"])
        rows = [
            "Ventas netas de bienes (o servicios)",
            "Costo de los bienes vendidos (o servicios prestados) (Anexo)",
            "Ganancia (Pérdida) bruta",
            "Resultado por valuación de bienes de cambio al VNR (Nota)",
            "Gastos de comercialización (Anexo)",
            "Gastos de administración (Anexo)",
            "Otros gastos (Anexo)",
            "Resultados de inversiones en entes relacionados (Nota)",
            "Resultados de otras inversiones (Nota)",
            "Resultados financieros y por tenencia (incluye RECPAM) - Generados por activos",
            "Resultados financieros y por tenencia (incluye RECPAM) - Generados por pasivos",
            "Otros ingresos y egresos (Nota)",
            "Ganancia (Pérdida) antes del impuesto a las ganancias",
            "Impuesto a las ganancias (Nota)",
            "Ganancia (Pérdida) ordinaria de las operaciones que continúan",
            "Resultados por operaciones en descontinuación (si corresponde)",
            "Ganancia (Pérdida) del ejercicio"
        ]
        w.writerow(["Detalle","Actual","Anterior"])
        for r in rows: w.writerow([r,"",""])

    # EEPN
    with (folder / "EEPN.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(_hdr(empresa, fecha))
        w.writerow(["ESTADO DE EVOLUCIÓN DEL PATRIMONIO NETO (RT 9)"])
        headers = ["Detalle","Capital Social","Ajustes Capital","Aportes Irrev.","Primas Emisión","Resultados Acum. - Ganancias Reservadas","Resultados Acum. - Diferidos","Resultados No Asignados","Totales - Actual","Totales - Anterior"]
        w.writerow(headers)
        movimientos = ["Saldos al inicio","Modificación saldos inicio (nota)","Saldos al inicio modificados","Suscripción de acciones","Capitalización de aportes irrevocables",
                       "Distribución de resultados no asignados > Reserva legal","Distribución > Otras reservas","Distribución > Dividendos (efectivo o especie)","Distribución > Dividendos en acciones",
                       "Desafectación de reservas","Aportes irrevocables","Absorción pérdidas acumuladas","Variación en resultados diferidos","Ganancia (Pérdida) del ejercicio","Saldos al cierre"]
        for m in movimientos: w.writerow([m]+[""]*(len(headers)-1))

    # EFE (según método)
    with (folder / "EFE.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(_hdr(empresa, fecha))
        w.writerow([f"ESTADO DE FLUJO DE EFECTIVO (Método {metodo_efe.capitalize()}) (RT 9)"])
        w.writerow(["Detalle","Actual","Anterior"])
        comunes = [
            "VARIACIÓN NETA DEL EFECTIVO",
            "Efectivo al inicio del ejercicio","Modificación de ejercicios anteriores (Nota)","Efectivo modificado al inicio (Nota)",
            "Efectivo al cierre del ejercicio (Nota)","Aumento (Disminución) neto(a) del efectivo",
            "CAUSAS DE LAS VARIACIONES DEL EFECTIVO"
        ]
        for r in comunes: w.writerow([r,"",""])
        if metodo_efe.lower() == "indirecto":
            oper = [
                "ACTIVIDADES OPERATIVAS",
                "Ganancia (Pérdida) ordinaria del ejercicio",
                "Intereses ganados y perdidos e impuesto a las ganancias devengados (Nota)",
                "Ajustes para arribar al flujo neto de efectivo por actividades operativas",
                "RF y por tenencia generados por el E y EE",
                "Depreciación de bienes de uso y activos intangibles",
                "Resultados relacionados con actividades de inversión y financiación (Nota)",
                "(Aumento) Disminución en créditos por ventas (Nota)",
                "(Aumento) Disminución en otros créditos (Nota)",
                "(Aumento) Disminución en bienes de cambio (Nota)",
                "Aumento (Disminución) en deudas operativas",
                "Pagos de intereses (Nota)",
                "Pagos del impuesto a las ganancias (Nota)",
                "Cobros de intereses (Nota)",
                "Flujo neto por actividades operativas"
            ]
        else:
            oper = [
                "ACTIVIDADES OPERATIVAS",
                "Cobros por ventas de bienes y servicios (Nota)",
                "Pagos por bienes y servicios operativos (Nota)",
                "Pagos al personal y cargas sociales",
                "Pagos de intereses (Nota)",
                "Pagos del impuesto a las ganancias (Nota)",
                "Cobros de intereses (Nota)",
                "Flujo neto por actividades operativas"
            ]
        for r in oper: w.writerow([r,"",""])
        inv = ["ACTIVIDADES DE INVERSIÓN","Pagos por compras de bienes de uso","Cobros por ventas de bienes de uso","Pagos por adquisición de participaciones (Nota)","Cobros de dividendos (Nota)","Flujo neto por actividades de inversión"]
        fin = ["ACTIVIDADES DE FINANCIACIÓN","Cobros por emisión de obligaciones negociables (Nota)","Cobros de aportes en efectivo de los propietarios","Cobros por préstamos tomados","Pagos por reembolsos de préstamos","Pagos de dividendos","Flujo neto por actividades de financiación"]
        for r in inv+fin: w.writerow([r,"",""])
        rf = ["RESULTADOS FINANCIEROS Y POR TENENCIA GENERADOS POR EL E Y EE","Diferencias de cambio","RECPAM sobre el efectivo y equivalentes","Neto por RF y p/T generados por el E y EE"]
        for r in rf: w.writerow([r,"",""])

def write_docx_templates(folder: Path, empresa: str, fecha: str, comparativo: bool, metodo_efe: str):
    from pathlib import Path
    import zipfile
    def make_docx(path: Path, title: str, body_lines: list[str]):
        from xml.sax.saxutils import escape
        def p(text):
            text = escape(text)
            return f'<w:p><w:r><w:t>{text}</w:t></w:r></w:p>'
        doc_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<w:document xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
                   'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                   '<w:body>' + p(title) + ''.join(p(l) for l in body_lines) + '<w:sectPr/></w:body></w:document>')
        rels_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
        content_types = ('<?xml version="1.0" encoding="UTF-8"?>'
                         '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                         '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                         '<Default Extension="xml" ContentType="application/xml"/>'
                         '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                         '</Types>')
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", content_types)
            z.writestr("_rels/.rels", rels_xml)
            z.writestr("word/document.xml", doc_xml)

    common = [f"Denominación: {empresa}", f"Fecha de corte: {fecha}", "Moneda homogénea", "Comparativo: Sí" if comparativo else "Comparativo: No"]
    make_docx(folder/"ESP.docx","ESP — Estado de Situación Patrimonial (RT 9)", common + ["Incluye: Activo Corriente/No Corriente, Pasivo Corriente/No Corriente, PN."])
    make_docx(folder/"EERR.docx","EERR — Estado de Resultados (RT 9)", common + ["Incluye: Ventas, Costos, Gastos, RF y por tenencia (RECPAM), Impuesto a las ganancias."])
    make_docx(folder/"EEPN.docx","EEPN — Estado de Evolución del Patrimonio Neto (RT 9)", common + ["Incluye: columnas por capital, ajustes, resultados acumulados, totales; movimientos: saldos inicio, distribuciones, variaciones, resultado del ejercicio."])
    make_docx(folder/"EFE.docx",f"EFE — Estado de Flujo de Efectivo (Método {metodo_efe.capitalize()}) (RT 9)", common + ["Incluye actividades Operativas, Inversión, Financiación, RF y p/T (diferencias de cambio y RECPAM)."])
    make_docx(folder/"Notas_complementarias.docx","Información complementaria y Anexos (RT 9)",
              common + [
                "Anexo: Activos y Pasivos en Moneda Extranjera",
                "Anexo: Inversiones en Títulos y Valores",
                "Anexo: Bienes de Uso",
                "Anexo: Propiedades de Inversión / Bienes depreciables",
                "Anexo: Participaciones en Sociedades",
                "Anexo: Activos Intangibles",
                "Anexo: Previsiones",
                "Anexo: Costo de bienes (servicios) vendidos",
                "Anexo: Información Art. 64 inc. b) Ley 19.550"
              ])
