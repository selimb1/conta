from typing import Dict

def propose_entry(campos: Dict) -> Dict:
    lineas = []
    neto_total = sum(campos.get("netos_por_alicuota",{}).values())
    iva_total = sum(campos.get("iva",{}).values())
    percep_iibb = campos.get("percepciones",{}).get("iibb",0)
    proveedor = campos.get("cuit_emisor","Proveedor")
    if neto_total:
        lineas.append({"cuenta":"110101","descripcion":"Mercaderías","debe":neto_total,"haber":0})
    if iva_total:
        lineas.append({"cuenta":"112101","descripcion":"IVA Crédito Fiscal","debe":iva_total,"haber":0})
    if percep_iibb:
        lineas.append({"cuenta":"113301","descripcion":"Percepciones IIBB","debe":percep_iibb,"haber":0})
    lineas.append({"cuenta":"210101","descripcion":f"Proveedores {proveedor}","debe":0,"haber":neto_total+iva_total+percep_iibb})
    return {"fecha": campos.get("fecha"), "lineas": lineas, "referencia_documento": "doc_uuid"}