
from __future__ import annotations
from typing import Dict, Any, List
from .valuation_policies import load_policies, match_policy
from datetime import date

def valuar_y_reexpresar(balances: List[Dict[str,Any]], fecha_corte: str) -> Dict[str,Any]:
    """
    balances: lista de dicts con {'cuenta':'1.1.1.01','desc':'Caja','saldo_historico':float,'moneda':'ARS','fx':1.0}
    fecha_corte: 'YYYY-MM-DD'
    Devuelve:
      - saldos_valuados (moneda de cierre)
      - asientos_ajuste (lista de movimientos)
      - papeles_trabajo (dicts por rubro)
    NOTA: Este es un motor determinístico simplificado para demo; el cálculo fino (índices, costo amortizado, VNR, VR) se enchufa por adaptadores.
    """
    pols = load_policies()
    asientos: List[Dict[str,Any]] = []
    salidas: List[Dict[str,Any]] = []
    papeles: Dict[str,Any] = {"inventarios":[],"bienes_de_uso":[],"intangibles":[],"creditos":[],"pasivos":[]}

    for row in balances:
        cuenta = row["cuenta"]
        pol = match_policy(cuenta, pols) or {"rubro":"Otros","posterior":"nominal"}
        saldo_hist = float(row.get("saldo_historico") or 0.0)

        # FX: convertir a tipo de cierre si moneda != ARS
        fx = float(row.get("fx") or 1.0)
        saldo_cierre = saldo_hist * fx  # stub para ejemplo

        ajuste = 0.0
        detalle = []

        # Reglas básicas por rubro
        rubro = pol["rubro"]
        if rubro == "Bienes de cambio":
            # min(costo, VNR) => si hay VNR suministrado en row['vnr']
            vnr = float(row.get("vnr") or saldo_cierre)
            nuevo_valor = min(saldo_cierre, vnr)
            ajuste = nuevo_valor - saldo_cierre
            detalle.append({"tipo":"VNR","vnr":vnr})
            papeles["inventarios"].append({"cuenta":cuenta,"costo":saldo_cierre,"vnr":vnr,"ajuste":ajuste})
        elif rubro == "Bienes de uso":
            # Depreciación simplificada anual si 'vida' y 'años_usados' presentes
            vida = float(row.get("vida_util") or 0) or None
            costo = float(row.get("costo") or saldo_cierre)
            amort_acum = float(row.get("amort_acum") or 0.0)
            if vida and vida > 0:
                # depreciación lineal del año: costo/vida
                dep = costo/vida
                nuevo_amort = amort_acum + dep
                nuevo_valor = costo - nuevo_amort
                ajuste = nuevo_valor - saldo_cierre
                detalle.append({"tipo":"Depreciación","dep_ejercicio":dep})
            papeles["bienes_de_uso"].append({"cuenta":cuenta,"costo":costo,"amort_acum":amort_acum})
        elif rubro == "Créditos":
            # Incobrabilidad esperada (si 'perdida_esp' % provista)
            pe = float(row.get("perdida_esp") or 0.0)
            ajuste = - abs(saldo_cierre * pe)
            detalle.append({"tipo":"Incobrabilidad","porcentaje":pe})
            papeles["creditos"].append({"cuenta":cuenta,"saldo":saldo_cierre,"pe":pe,"ajuste":ajuste})
        elif rubro.startswith("Pasivos"):
            # Costo amortizado y FX ya contemplados; sin ajuste adicional en stub
            papeles["pasivos"].append({"cuenta":cuenta,"saldo":saldo_cierre})
        elif rubro == "Intangibles":
            vida = float(row.get("vida_util") or 0) or None
            costo = float(row.get("costo") or saldo_cierre)
            amort_acum = float(row.get("amort_acum") or 0.0)
            if vida and vida > 0:
                amort = costo/vida
                nuevo_valor = costo - (amort_acum + amort)
                ajuste = nuevo_valor - saldo_cierre
                detalle.append({"tipo":"Amortización","amort_ejercicio":amort})
            papeles["intangibles"].append({"cuenta":cuenta,"costo":costo,"amort_acum":amort_acum})

        # RECPAM/Inflación: se registrará como parte de resultados financieros; aquí sólo marcamos placeholder
        if pol.get("ajuste_inflacion"):
            detalle.append({"tipo":"RECPAM_placeholder":"se calcula con índices oficiales"})

        saldo_ajustado = saldo_cierre + ajuste
        salidas.append({
            "cuenta": cuenta,
            "desc": row.get("desc",""),
            "rubro": rubro,
            "saldo_historico": saldo_hist,
            "saldo_cierre": saldo_cierre,
            "ajuste": ajuste,
            "saldo_valuado": saldo_ajustado,
            "detalle": detalle
        })

        if ajuste != 0.0:
            # Asiento de ajuste por cuenta (simplificado): contra Resultados por valuación / RECPAM segun rubro
            if rubro in ("Bienes de cambio","Créditos"):
                resultado_cta = "5.9.1. Ajustes de valuación"
            elif rubro in ("Bienes de uso","Intangibles"):
                resultado_cta = "5.9.2. Amort./Depreciación"
            else:
                resultado_cta = "5.9.9. Resultados por tenencia/RECPAM"
            asientos.append({
                "fecha": fecha_corte,
                "detalle": f"Ajuste valuación {rubro} - {cuenta}",
                "movimientos":[
                    {"cuenta": cuenta, "debe": max(ajuste,0), "haber": max(-ajuste,0)},
                    {"cuenta": resultado_cta, "debe": max(-ajuste,0), "haber": max(ajuste,0)}
                ]
            })

    return {
        "saldos_valuados": salidas,
        "asientos_ajuste": asientos,
        "papeles_trabajo": papeles
    }
