"""Evalua SLO y aplica supresion de duplicados. No envia mensajes externos."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from .common import ROOT, load_config, load_json, utcnow, write_json


def evaluar_alertas(metrics: dict, config: dict) -> list[dict]:
    s = config["slo"]
    a = config["alertas"]
    alerts: list[dict] = []
    def add(code: str, severity: str, value, limit, action: str):
        alerts.append({"codigo":code,"severidad":severity,"observado":value,
                       "umbral":limit,"accion_sugerida":action,"momento_utc":utcnow()})

    n = metrics.get("n_ventana", 0)
    if n >= a["muestras_minimas_disponibilidad"]:
        d = metrics.get("disponibilidad")
        if d is not None and d < s["disponibilidad_min"]:
            add("SLO_DISPONIBILIDAD", "P1", d, s["disponibilidad_min"], "Ejecutar RB-01; comprobar /health")
        e = metrics.get("error_5xx_rate")
        if e is not None and e > s["error_http_5xx_max"]:
            add("ERRORES_5XX", "P1", e, s["error_http_5xx_max"], "Ejecutar RB-01; no reintentar sin limite")
    latency = metrics.get("latencia_p95_ms")
    if latency is not None and metrics.get("n_latencia",0) >= 5 and latency > s["latencia_p95_ms_max"]:
        add("LATENCIA_P95", "P2", latency, s["latencia_p95_ms_max"], "Ejecutar RB-02")
    fe = metrics.get("falsas_elegibilidades")
    if fe is not None and fe > s["falsas_elegibilidades_max"]:
        add("FALSA_ELEGIBILIDAD", "P0", fe, s["falsas_elegibilidades_max"], "Detener aceptacion automatica en escenario controlado y escalar")
    psi = metrics.get("drift_psi")
    if psi is not None and metrics.get("n_drift",0) >= a["muestras_minimas_drift"]:
        if psi >= s["drift_psi_critical"]:
            add("DRIFT_CRITICO", "P1", psi, s["drift_psi_critical"], "Ejecutar RB-03; verificar etiquetas")
        elif psi >= s["drift_psi_warning"]:
            add("DRIFT_ADVERTENCIA", "P2", psi, s["drift_psi_warning"], "Revisar distribucion y preparar evaluacion")
    return alerts


def deduplicar(alerts: list[dict], state: dict, cooldown_minutes: int, now: datetime | None = None) -> tuple[list[dict],dict]:
    now = now or datetime.now(timezone.utc)
    updated = dict(state)
    published = []
    for alert in alerts:
        code=alert["codigo"]
        last = updated.get(code)
        if last:
            try:
                when=datetime.fromisoformat(last)
                if when.tzinfo is None:
                    when=when.replace(tzinfo=timezone.utc)
                if now-when < timedelta(minutes=cooldown_minutes):
                    continue
            except ValueError:
                pass
        updated[code] = now.isoformat()
        published.append(alert)
    return published, updated


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--metricas", type=Path, default=ROOT/"results"/"metricas"/"resumen.json")
    p.add_argument("--salida", type=Path, default=ROOT/"results"/"metricas"/"alertas.json")
    p.add_argument("--estado", type=Path, default=ROOT/"results"/"metricas"/"estado_alertas.json")
    args=p.parse_args()
    cfg=load_config()
    metrics=load_json(args.metricas)
    if metrics is None:
        raise SystemExit("Falta archivo de metricas")
    candidates=evaluar_alertas(metrics,cfg)
    prior={"P0":0,"P1":1,"P2":2}
    candidates.sort(key=lambda x: prior.get(x["severidad"],9))
    published,state=deduplicar(candidates,load_json(args.estado,{}),cfg["alertas"]["cooldown_minutos"])
    write_json(args.estado,state)
    write_json(args.salida,{"generadas":len(candidates),"emitidas":published,"suprimidas":len(candidates)-len(published)})
    print(f"Alertas candidatas={len(candidates)}; emitidas={len(published)}; suprimidas={len(candidates)-len(published)}")

if __name__ == "__main__":
    main()
