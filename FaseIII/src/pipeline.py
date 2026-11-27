"""CIMA Fase III - evidence-first, offline-safe MLOps validation.
Usage: python -m src.pipeline --repo-root .. --out evidencias/pipeline
No deployment, model execution or external calls occur here.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

LABELS = {'INDIVIDUAL', 'PAQUETE', 'AMBIGUA', 'FUERA_ALCANCE'}
REQUIRED = {'id','texto','clase_real'}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def validate_data(path: Path) -> dict:
    with path.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
            raise ValueError('Faltan columnas obligatorias id,texto,clase_real')
        rows = list(reader)
    if not rows:
        raise ValueError('Dataset vacio')
    ids = [r['id'].strip() for r in rows]
    if any(not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('Identificadores vacios o repetidos')
    if any(not r['texto'].strip() for r in rows):
        raise ValueError('Consulta vacia')
    if any(r['clase_real'].strip() not in LABELS for r in rows):
        raise ValueError('Etiqueta desconocida')
    labels = {k: sum(r['clase_real'].strip() == k for r in rows) for k in sorted(LABELS)}
    return {'filas': len(rows), 'distribucion': labels, 'sha256': sha256(path),
            'n_textos_repetidos': len(rows) - len(set(r['texto'].strip().lower() for r in rows))}


def git_rev(repo: Path) -> str | None:
    try:
        return subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],stderr=subprocess.DEVNULL,text=True).strip()
    except (subprocess.CalledProcessError,FileNotFoundError):
        return None


def inventory(repo: Path, artifact_paths: list[str]) -> list[dict]:
    results=[]
    for rel in artifact_paths:
        p = repo / rel
        results.append({'ruta':rel,'existe':p.is_file(), 'bytes':p.stat().st_size if p.is_file() else None,
                        'sha256':sha256(p) if p.is_file() else None})
    return results


def build(repo: Path, data: Path, out: Path, version: str) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    artifacts=['FaseII/Dockerfile','FaseII/requirements.txt','FaseII/backend/main.py',
               'FaseII/backend/classifier.py','FaseII/modelos/Regresion_Logistica.joblib',
               'Actividad8/README.md']
    manifest={'schema_version':'1.0','fase':'III','proyecto':'CIMA','modelo_version_declarada':version,
        'created_utc':datetime.now(timezone.utc).isoformat(),'repo_commit':git_rev(repo),
        'origen':'INVENTARIO_REPOSITORIO','datos':validate_data(data),
        'artefactos':inventory(repo,artifacts),
        'reglas_de_publicacion':['Pruebas CI satisfactorias','Revision y aprobacion humana','Sin datos bancarios reales'],
        'automatic_deployment_executed':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    observed=sum(item['existe'] for item in manifest['artefactos'])
    print(f"[OK] Dataset validado: {manifest['datos']['filas']} registros")
    print(f'[INFO] Artefactos encontrados: {observed}/{len(artifacts)}')
    for item in manifest['artefactos']:
        if not item['existe']:
            print(f"[ADVERTENCIA] No encontrado: {item['ruta']}; verificar nombre/ruta del repo")
    print(f'[OK] Manifiesto: {out / "manifest.json"}')
    return manifest


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'data'/'consultas_sinteticas.csv')
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'evidencias'/'pipeline')
    parser.add_argument('--model-version',default='actividad5-regresion-logistica-a5-v1.0')
    a=parser.parse_args()
    build(a.repo_root.resolve(),a.data.resolve(),a.out.resolve(),a.model_version)
if __name__=='__main__':main()
