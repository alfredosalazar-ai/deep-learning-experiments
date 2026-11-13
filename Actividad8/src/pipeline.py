"""Ejecuta evaluacion de alertas con metricas existentes y PSI si esta disponible.
No consulta internet; uso offline y postproceso de una medicion ya exportada.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from .alertas import deduplicar, evaluar_alertas
from .common import ROOT,load_config,load_json,write_json
from .dashboard import render


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--simulado",action="store_true",help="Usa metricas artificiales para demo, no afirma medicion real")
    args=p.parse_args()
    cfg=load_config()
    results=ROOT/"results"
    if args.simulado:
        metrics={"origen":"SIMULACION_AISLADA","n_ventana":50,"disponibilidad":0.96,
                 "error_5xx_rate":0.04,"n_latencia":30,"latencia_p95_ms":6500,
                 "n_drift":100,"drift_psi":0.8,"falsas_elegibilidades":1}
        folder=results/"incidentes"
        out=folder/"metricas_demo.json"
        alertout=folder/"alertas_demo.json"
        board=results/"dashboards"/"dashboard_simulado.html"
    else:
        metrics=load_json(results/"metricas"/"resumen.json")
        if metrics is None:
            raise SystemExit("Faltan metricas reales: ejecutar antes python -m src.monitor --solo-health")
        drift=load_json(results/"metricas"/"drift.json")
        if drift:
            metrics.update({k:drift[k] for k in ("drift_psi","n_drift") if k in drift})
        folder=results/"metricas"
        out=folder/"resumen_con_drift.json"
        alertout=folder/"alertas.json"
        board=results/"dashboards"/"dashboard.html"
    candidates=evaluar_alertas(metrics,cfg)
    statefile=folder/("estado_alertas_demo.json" if args.simulado else "estado_alertas.json")
    emitted,state=deduplicar(candidates,load_json(statefile,{}),cfg["alertas"]["cooldown_minutos"])
    alert_info={"generadas":len(candidates),"emitidas":emitted,"suprimidas":len(candidates)-len(emitted),
                "nota":"Las respuestas correctivas son recomendaciones; no cambia estado de Render ni del modelo."}
    write_json(out,metrics);write_json(alertout,alert_info);write_json(statefile,state)
    board.parent.mkdir(parents=True,exist_ok=True)
    board.write_text(render(metrics,alert_info,load_json(results/"incidentes"/"simulacion.json",{})),encoding="utf-8")
    print(f"Origen: {'SIMULADO' if args.simulado else 'SONDEO HTTP'}; alertas emitidas={len(emitted)}; dashboard={board}")

if __name__=="__main__":main()
