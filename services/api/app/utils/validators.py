from typing import Dict, List

def validate_fields(campos: Dict) -> List[Dict]:
    out = []
    def add(rule, sev, ok, msg):
        out.append({"regla": rule, "severidad": sev, "passed": ok, "mensaje": msg})
    # ejemplos
    add("total_presente", "error", campos.get("total") is not None, "Total presente")
    if campos.get("netos_por_alicuota") and campos.get("iva") and campos.get("total") is not None:
        suma = sum(campos["netos_por_alicuota"].values()) + sum(campos["iva"].values()) + campos.get("exento",0) + campos.get("no_gravado",0) + sum(campos.get("percepciones",{}).values())
        add("totales_cierran", "error", abs(suma - campos["total"]) < 0.01, "La suma cierra con el total")
    return out