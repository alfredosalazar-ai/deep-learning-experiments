"""Simulacion local determinista: NO genera fallas en Render."""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
from .alertas import evaluar_alertas
from .common import ROOT, load_config, utcnow, write_json
from .drift import CLASSES, population_stability_index


def simular_incidentes(config:dict) -> dict:
    baseline={x:25 for x in CLASSES}
    shifted={"INDIVIDUAL":1,"PAQUETE":2,"AMBIGUA":2,"FUERA_ALCANCE":95}
    drift=population_stability_index(baseline,shifted)
    # INC-01: latencia; INC-02: drift; INC-03: interrupcion HTTP
    scenarios=[
        {"id":"INC-01","nombre":"Latencia artificial","antes":{"n_ventana":50,"disponibilidad":1.0,"error_5xx_rate":0,"latencia_p95_ms":450,"n_latencia":30},
         "durante":{"n_ventana":50,"disponibilidad":1.0,"error_5xx_rate":0,"latencia_p95_ms":7200,"n_latencia":30},
         "despues":{"n_ventana":50,"disponibilidad":1.0,"error_5xx_rate":0,"latencia_p95_ms":520,"n_latencia":30},"runbook":"RB-02", "accion":"Aislar carga sintetica; reducir concurrencia y comparar el P95"},
        {"id":"INC-02","nombre":"Drift sintetico de clases","antes":{"n_ventana":50,"disponibilidad":1.0,"error_5xx_rate":0,"n_drift":100,"drift_psi":0.0},
         "durante":{"n_ventana":50,"disponibilidad":1.0,"error_5xx_rate":0,"n_drift":100,"drift_psi":drift},
         "despues":{"n_ventana":50,"disponibilidad":1.0,"error_5xx_rate":0,"n_drift":100,"drift_psi":0.0},"runbook":"RB-03","accion":"Suspender aceptacion simulada, revisar referencia y restaurar mezcla sintetica"},
        {"id":"INC-03","nombre":"Fallas HTTP 503 artificiales","antes":{"n_ventana":100,"disponibilidad":1.0,"error_5xx_rate":0.0},
         "durante":{"n_ventana":100,"disponibilidad":0.8,"error_5xx_rate":0.2},
         "despues":{"n_ventana":100,"disponibilidad":1.0,"error_5xx_rate":0.0},"runbook":"RB-01","accion":"Activar contingencia simulada y reintentos limitados; restablecer servicio ficticio"}
    ]
    output=[]
    for sc in scenarios:
        before=evaluar_alertas(sc["antes"],config)
        during=evaluar_alertas(sc["durante"],config)
        after=evaluar_alertas(sc["despues"],config)
        output.append({"id":sc["id"],"nombre":sc["nombre"],"tipo":"SIMULACION_AISLADA",
                       "fecha_utc":utcnow(),"antes":sc["antes"],"alertas_antes":before,
                       "durante":sc["durante"],"alertas_durante":during,
                       "runbook_ejecutado_simulado":sc["runbook"],"accion_simulada":sc["accion"],
                       "despues":sc["despues"],"alertas_despues":after,
                       "recuperacion_simulada":bool(during and not after)})
    return {"origen":"SIMULACION_OFFLINE", "modelo_en_render_modificado":False,
            "nota":"Resultados fabricados para verificar la logica de alertas y runbooks; NO son incidentes reales.",
            "incidentes":output}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--salida",type=Path,default=ROOT/"results"/"incidentes"/"simulacion.json")
    args=p.parse_args()
    result=simular_incidentes(load_config())
    write_json(args.salida,result)
    for x in result["incidentes"]:
        print(f'{x["id"]}: alertas durante={len(x["alertas_durante"])}, despues={len(x["alertas_despues"])}, recuperacion simulada={x["recuperacion_simulada"]}')

if __name__=="__main__":main()
