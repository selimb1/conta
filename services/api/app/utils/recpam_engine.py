
from __future__ import annotations
from typing import List, Dict, Any
from .inflacion import coef

def reexpresar_moneda_cierre(movimientos: List[Dict[str,Any]], fecha_cierre: str):
    """
    movimientos: [{'fecha':'YYYY-MM-DD','cuenta':'X','importe':float}...] (saldos o movimientos históricos)
    Devuelve:
      - movimientos_reexpresados (moneda de cierre)
      - recpam_total por cuenta y global
    Método simplificado: multiplica cada importe histórico por coef(fecha_mov, fecha_cierre).
    """
    reexp: List[Dict[str,Any]] = []
    recpam_por_cta: Dict[str, float] = {}
    for m in movimientos:
        cta = m["cuenta"]
        imp = float(m["importe"])
        f = m["fecha"]
        k = coef(f, fecha_cierre)
        imp_reexp = imp * k
        delta = imp_reexp - imp
        reexp.append({**m, "coef":k, "importe_reexp": imp_reexp, "recpam": delta})
        recpam_por_cta[cta] = recpam_por_cta.get(cta, 0.0) + delta
    recpam_total = sum(recpam_por_cta.values())
    return {"movimientos_reexpresados": reexp, "recpam_por_cta": recpam_por_cta, "recpam_total": recpam_total}
