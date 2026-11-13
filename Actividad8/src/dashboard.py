"""Genera dashboard HTML estatico de ultimo resultado; no es tiempo real."""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
from .common import ROOT, load_json


def render(metrics:dict, alerts:dict, incidents:dict) -> str:
    def pretty(v):
        if v is None:return "Sin datos"
        if isinstance(v,float):return f"{v:.3f}"
        return str(v)
    cells="".join(f'<section><small>{html.escape(str(k).replace("_"," "))}</small><strong>{html.escape(pretty(v))}</strong></section>'
                  for k,v in metrics.items() if k in ("n_ventana","disponibilidad","latencia_p95_ms","error_5xx_rate","n_predict","falsas_elegibilidades"))
    ar=alerts.get("emitidas",[])
    al="".join(f'<tr><td>{html.escape(x["severidad"])}</td><td>{html.escape(x["codigo"])}</td><td>{html.escape(pretty(x["observado"]))}</td></tr>' for x in ar)
    inc="".join(f'<tr><td>{html.escape(x["id"])}</td><td>{html.escape(x["nombre"])}</td><td>{"Si (simulado)" if x["recuperacion_simulada"] else "No"}</td></tr>' for x in incidents.get("incidentes",[]))
    return f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CIMA A8 - Observabilidad</title><style>body{{font-family:system-ui;margin:2rem auto;max-width:1100px;background:#f3f6f9;color:#142b48;padding:0 1rem}}header{{background:#0b345b;color:white;padding:2rem;border-radius:12px}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:24px 0}}section{{background:white;border:1px solid #d5e0ed;border-radius:9px;padding:16px}}small{{display:block;color:#60758d;margin-bottom:8px}}strong{{font-size:23px}}table{{border-collapse:collapse;width:100%;background:white}}th,td{{text-align:left;border-bottom:1px solid #d5e0ed;padding:10px}}p{{line-height:1.5}}.note{{border-left:4px solid #b17822;padding:12px;background:#fff7e7}}</style><header><h1>CHATBOT CIMA · Actividad 8</h1><p>Panel de resultados académicos — archivo estático, NO monitoreo en tiempo real</p></header><h2>Última medición</h2><div class="grid">{cells}</div><p class="note">Cuando no hay mediciones HTTP reales, este panel puede mostrar solamente simulaciones. No interpretar como disponibilidad de producción. Fuente de medición: {html.escape(str(metrics.get("fuente","no disponible")))}</p><h2>Alertas emitidas</h2><table><thead><tr><th>Severidad</th><th>Código</th><th>Valor</th></tr></thead><tbody>{al or '<tr><td colspan="3">Sin alertas emitidas</td></tr>'}</tbody></table><h2>Incidentes de laboratorio</h2><table><thead><tr><th>ID</th><th>Escenario</th><th>Recuperación</th></tr></thead><tbody>{inc or '<tr><td colspan="3">Sin simulaciones</td></tr>'}</tbody></table></html>'''


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--salida",type=Path,default=ROOT/"results"/"dashboards"/"dashboard.html")
    args=p.parse_args()
    path=ROOT/"results"
    result=render(load_json(path/"metricas"/"resumen.json",{}),load_json(path/"metricas"/"alertas.json",{}),load_json(path/"incidentes"/"simulacion.json",{}))
    args.salida.parent.mkdir(parents=True,exist_ok=True)
    args.salida.write_text(result,encoding="utf-8")
    print(f"Dashboard estatico: {args.salida}")

if __name__=="__main__":main()
