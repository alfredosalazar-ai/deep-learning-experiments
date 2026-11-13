"""PSI sobre distribucion de clases predichas. Detecta cambio, no calidad real."""
from __future__ import annotations
import argparse
import csv
import math
from pathlib import Path
from .common import ROOT, load_config, utcnow, write_json

CLASSES = ("INDIVIDUAL","PAQUETE","AMBIGUA","FUERA_ALCANCE")


def population_stability_index(ref: dict[str, int], cur: dict[str, int], epsilon: float = 1e-5) -> float:
    if sum(ref.values()) <= 0 or sum(cur.values()) <= 0:
        raise ValueError("La distribucion debe incluir observaciones")
    n_ref=sum(ref.values()); n_cur=sum(cur.values())
    result=0.0
    for cls in CLASSES:
        p=max(ref.get(cls,0)/n_ref,epsilon)
        q=max(cur.get(cls,0)/n_cur,epsilon)
        result+=(q-p)*math.log(q/p)
    return result


def count_csv(path:Path,column:str) -> dict[str,int]:
    c={x:0 for x in CLASSES}
    with path.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        if column not in (reader.fieldnames or []):
            raise ValueError(f"Falta columna {column} en {path}")
        for row in reader:
            cls=row[column]
            if cls not in c:
                raise ValueError(f"Clase inesperada: {cls}")
            c[cls]+=1
    return c


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--referencia",type=Path,required=True)
    p.add_argument("--actual",type=Path,required=True)
    p.add_argument("--columna",default="clase_predicha")
    p.add_argument("--salida",type=Path,default=ROOT/"results"/"metricas"/"drift.json")
    args=p.parse_args()
    ref=count_csv(args.referencia,args.columna)
    cur=count_csv(args.actual,args.columna)
    psi=population_stability_index(ref,cur)
    cfg=load_config()
    severity="critico" if psi>=cfg["slo"]["drift_psi_critical"] else "advertencia" if psi>=cfg["slo"]["drift_psi_warning"] else "sin_alerta"
    write_json(args.salida,{"momento_utc":utcnow(),"drift_psi":psi,"n_drift":sum(cur.values()),"referencia":ref,"actual":cur,"clasificacion":severity,"nota":"PSI mide cambio de distribucion; no demuestra degradacion predictiva sin etiquetas."})
    print(f"PSI={psi:.4f} | Estado={severity}")

if __name__=="__main__":
    main()
