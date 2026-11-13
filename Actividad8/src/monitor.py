"""Sondeo bajo demanda de CIMA. Sin datos reales ni modificaciones en Render.

Ejecucion recomendada desde la raiz del repositorio:
 python -m src.monitor --solo-health
 python -m src.monitor --incluye-predict --consultas 4
"""
from __future__ import annotations
import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import uuid4
from .common import ROOT, append_jsonl, load_config, percentile_nearest_rank, public_base, utcnow, write_json

SYNTHETIC = [
    {"id":"MON-001","texto":"Solicito confirmar el pago del folio ficticio 12345.","esperada":"INDIVIDUAL"},
    {"id":"MON-002","texto":"Revisar el paquete de 15 folios simulados.","esperada":"PAQUETE"},
    {"id":"MON-003","texto":"Tengo un deposito sin folio ni referencia.","esperada":"AMBIGUA"},
    {"id":"MON-004","texto":"Quiero cotizar unas vacaciones en la playa.","esperada":"FUERA_ALCANCE"},
]


def request(url:str, method:str="GET", json_data:dict|None=None, timeout:float=20.0) -> dict:
    payload=json.dumps(json_data).encode("utf-8") if json_data is not None else None
    headers={"Accept":"application/json","User-Agent":"CIMA-A8-Monitor-Academico/1.0"}
    if payload is not None:
        headers["Content-Type"]="application/json"
    req=urllib.request.Request(url,data=payload,headers=headers,method=method)
    t0=time.perf_counter()
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            status=r.status
            raw=r.read(16384)
            data=json.loads(raw.decode("utf-8"))
            if not isinstance(data,dict):
                data={"respuesta_no_objeto":True}
            return {"status":status,"body":data,"duration_ms":(time.perf_counter()-t0)*1000,"error":None}
    except urllib.error.HTTPError as e:
        return {"status":e.code,"body":{},"duration_ms":(time.perf_counter()-t0)*1000,"error":f"HTTP {e.code}"}
    except (urllib.error.URLError,TimeoutError,ValueError,UnicodeDecodeError) as e:
        return {"status":None,"body":{},"duration_ms":(time.perf_counter()-t0)*1000,"error":type(e).__name__}


def summarize(records: list[dict], exclude_warmup:bool=True) -> dict:
    # Disponibilidad: /health con 2xx y model_loaded=true (otros codigos son error).
    health=[r for r in records if r["endpoint"]=="/health"]
    total=len(health)
    success=sum(1 for r in health if r["ok"])
    n_5xx=sum(1 for r in records if r.get("status") and r["status"]>=500)
    pred=[r for r in records if r["endpoint"]=="/predict"]
    eligible=[r for r in pred if r.get("decision_operativa")=="CONSULTA_INDIVIDUAL_ELEGIBLE"]
    # Politica no confirmada en codigo fuente: los campos determinan la aceptacion.
    # Una decision no REVISION_HUMANA se analiza como potencial aceptacion.
    accepted=[r for r in pred if r.get("decision_operativa") and r["decision_operativa"]!="REVISION_HUMANA"]
    false_eligible=sum(1 for r in accepted if r.get("clase_esperada")!="INDIVIDUAL")
    # P95 de inferencia HTTP, excluye warmup y fallas. Al menos 5 muestras para alertar.
    latencies=[r["duration_ms"] for r in pred if r.get("ok") and not (exclude_warmup and r.get("warmup"))]
    return {
        "momento_utc":utcnow(),"tipo_medicion":"real_http_si_no_es_simulacion",
        "n_ventana":total,"health_ok":success,
        "fallos_health":total-success,
        "disponibilidad":success/total if total else None,
        "error_5xx_rate":n_5xx/len(records) if records else None,
        "n_http":len(records),"n_predict":len(pred),"n_latencia":len(latencies),
        "latencia_p95_ms":percentile_nearest_rank(latencies,.95),
        "aceptados_automaticamente":len(accepted),
        "falsas_elegibilidades":false_eligible if pred else None,
        "n_etiquetados":len([r for r in pred if r.get("clase_esperada")]),
        "nota":"Muestra sintetica de sondeo, no estimacion de generalizacion ni SLO mensual."
    }


def main():
    p=argparse.ArgumentParser(description="Sondeo sin informacion bancaria")
    p.add_argument("--base-url",default=None)
    group=p.add_mutually_exclusive_group()
    group.add_argument("--solo-health",action="store_true")
    group.add_argument("--incluye-predict",action="store_true")
    p.add_argument("--consultas",type=int,default=4)
    p.add_argument("--health-checks",type=int,default=3)
    p.add_argument("--pausa-segundos",type=float,default=0)
    p.add_argument("--timeout",type=float,default=20)
    p.add_argument("--salida",type=Path,default=ROOT/"results"/"metricas")
    args=p.parse_args()
    if not 0<=args.consultas<=4 or not 1<=args.health_checks<=20 or not 0<=args.pausa_segundos<=10:
        p.error("Fuera de rango: consultas 0-4, health-checks 1-20 y pausa 0-10")
    cfg=load_config()
    url=public_base(args.base_url or cfg["service_url"])
    records=[]
    # Primera solicitud solo para despertar Render Free; no entra al SLO de inferencia.
    for i in range(args.health_checks):
        r=request(url+"/health",timeout=args.timeout)
        record={"trace_id":str(uuid4()),"momento_utc":utcnow(),"endpoint":"/health",
                "warmup":i==0,"status":r["status"],"duration_ms":round(r["duration_ms"],3),
                "ok":bool(r["status"]==200 and r["body"].get("model_loaded") is True and r["body"].get("status")=="ok"),
                "error":r["error"]}
        records.append(record)
        if args.pausa_segundos: time.sleep(args.pausa_segundos)
    if args.incluye_predict:
        for sample in SYNTHETIC[:args.consultas]:
            r=request(url+"/predict",method="POST",json_data={"texto":sample["texto"]},timeout=args.timeout)
            body=r["body"]
            record={"trace_id":str(uuid4()),"momento_utc":utcnow(),"endpoint":"/predict",
                "id_sintetico":sample["id"],"clase_esperada":sample["esperada"],
                "longitud_texto":len(sample["texto"]),"status":r["status"],
                "duration_ms":round(r["duration_ms"],3),"warmup":False,
                "ok":r["status"]==200 and "clase_predicha" in body,
                "clase_predicha":body.get("clase_predicha"),
                "decision_operativa":body.get("decision_operativa"),
                "puntaje_individual":body.get("puntaje_individual"),
                "umbral_individual":body.get("umbral_individual"),"error":r["error"]}
            records.append(record)
            if args.pausa_segundos: time.sleep(args.pausa_segundos)
    args.salida.mkdir(parents=True,exist_ok=True)
    # Version de salida por invocacion; no sobreescribe mediciones previas.
    runid=utcnow().replace(":", "-")+"_"+uuid4().hex[:8]
    logfile=args.salida/f"mediciones_{runid}.jsonl"
    for rec in records: append_jsonl(logfile,rec)
    summary=summarize(records,cfg["alertas"]["excluir_warmup_latencia"])
    # Budget exacto dentro de esta ventana: numero de fallas tolerables por SLO.
    # En ventanas pequenas es indicativo y no sustituye SLO mensuales.
    allowed=int((1-cfg["slo"]["disponibilidad_min"])*summary["n_ventana"]+1e-9)
    summary["error_budget_fallos_permitidos"] = allowed
    summary["error_budget_fallos_consumidos"] = summary["fallos_health"]
    summary["error_budget_fallos_restantes"] = max(0,allowed-summary["fallos_health"])
    summary["error_budget_excedido"] = summary["fallos_health"]>allowed
    summary["fuente"] = url
    summary["archivo_registros"] = logfile.name
    write_json(args.salida/"resumen.json",summary)
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    print("EVIDENCIA REAL solo si esta ejecucion ha llamado a la URL indicada; no equivale a monitoreo continuo.")

if __name__=="__main__":
    main()
