"""Registro reproducible en MLflow de las SIMULACIONES de Actividad 8.

Uso desde Actividad8/:
 python -m src.mlflow_registro --input /content/cima-a8-simulacion.zip \
   --tracking-dir /content/cima_mlflow --workflow-run 4 --commit c0d6991

No llama ni altera Render, no reentrena ni publica modelos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, BadZipFile

REQUIRED = (
    'incidentes/simulacion.json',
    'incidentes/runbooks_ejecutados_demo.json',
    'incidentes/alertas_demo.json',
    'incidentes/metricas_demo.json',
    'metricas/calidad_demo.json',
)
EXTRA = (
    'incidentes/consola_alertas_demo.txt',
    'dashboards/dashboard_simulado.html',
    'dashboards/INC-01_indicador.png',
    'dashboards/INC-02_indicador.png',
    'dashboards/INC-03_indicador.png',
    'dashboards/calidad_simulada.png',
)
EXPERIMENT = 'CIMA_Actividad8_Observabilidad_Simulada'


def leer_zip(archivo: Path):
    with ZipFile(archivo) as z:
        names = set(z.namelist())
        missing = sorted(set(REQUIRED) - names)
        if missing:
            raise ValueError('Faltan archivos obligatorios del artefacto: ' + ', '.join(missing))
        objetos = {p: json.loads(z.read(p)) for p in REQUIRED}
        for p in REQUIRED:
            if objetos[p].get('origen') not in ('SIMULACION_OFFLINE', 'SIMULACION_AISLADA', None):
                raise ValueError(f'Origen inesperado en {p}: {objetos[p].get("origen")}')
        sim = objetos['incidentes/simulacion.json']
        if sim.get('origen') != 'SIMULACION_OFFLINE' or sim.get('modelo_en_render_modificado') is not False:
            raise ValueError('El artefacto no confirma simulacion offline sin alterar Render')
        if len(sim.get('incidentes', [])) < 2:
            raise ValueError('La rubrica exige al menos dos incidentes; faltan escenarios')
        return objetos, {p: z.read(p) for p in (*REQUIRED, *EXTRA) if p in names}


def numero(x):
    return isinstance(x, (int,float)) and not isinstance(x,bool) and math.isfinite(x)


def registrar(input_zip: Path, tracking_dir: Path, workflow_run: str='', commit: str=''):
    import mlflow
    from mlflow.tracking import MlflowClient

    input_zip = input_zip.expanduser().resolve()
    tracking_dir = tracking_dir.expanduser().resolve()
    if not input_zip.is_file():
        raise FileNotFoundError(f'No se encontro el artefacto: {input_zip}')
    tracking_dir.mkdir(parents=True, exist_ok=True)
    objetos, anexos = leer_zip(input_zip)
    sha = hashlib.sha256(input_zip.read_bytes()).hexdigest()

    # Almacen local de Colab: la persistencia requiere descargar su archivo ZIP.
    uri = (tracking_dir / 'mlruns').as_uri()
    mlflow.set_tracking_uri(uri)
    experiment = mlflow.set_experiment(EXPERIMENT)
    common = {
        'origen': 'SIMULACION_OFFLINE',
        'fuente': 'GITHUB_ACTIONS_ARTIFACTO_DESCARGADO',
        'modifica_render': 'NO',
        'entorno': 'GOOGLE_COLAB',
        'sha256_artefacto': sha,
    }
    if workflow_run: common['workflow_run_declarado'] = workflow_run
    if commit: common['commit_declarado'] = commit
    run_ids = []
    sim = objetos['incidentes/simulacion.json']
    runs_book = objetos['incidentes/runbooks_ejecutados_demo.json']
    quality = objetos['metricas/calidad_demo.json']
    metadata = {'sha256_zip':sha, 'experiment_id':experiment.experiment_id,
                'tracking_uri':uri,'runs':[]}

    # Almacenar primero artefactos localmente con nombres exactos, sin extraer el ZIP
    # mediante extractall() (evita rutas internas maliciosas).
    with TemporaryDirectory() as temp:
        tmp = Path(temp)
        for name, raw in anexos.items():
            target = tmp / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
        for caso in sim['incidentes']:
            ident = str(caso['id'])
            run_name = f'{ident}_incidente_offline'
            with mlflow.start_run(run_name=run_name) as run:
                mlflow.set_tags({**common,'tipo_run':'INCIDENTE','incidente':ident,
                                 'runbook':str(caso.get('runbook_ejecutado_simulado',''))})
                mlflow.log_params({'escenario':str(caso.get('nombre',''))[:250],
                                  'n_ventana':int(caso['durante'].get('n_ventana',0))})
                for fase, step in [('antes',0),('durante',1),('despues',2)]:
                    datos = caso.get(fase,{})
                    for campo in ('latencia_p95_ms','drift_psi','disponibilidad','error_5xx_rate'):
                        val = datos.get(campo)
                        if numero(val): mlflow.log_metric(campo, float(val), step=step)
                    mlflow.log_metric('alertas_activas',len(caso.get('alertas_'+fase,[])),step=step)
                mlflow.log_metric('recuperacion_simulada',int(bool(caso.get('recuperacion_simulada'))))
                mlflow.log_artifact(str(tmp/'incidentes/simulacion.json'), artifact_path='fuente')
                imagen = tmp/f'dashboards/{ident}_indicador.png'
                if imagen.is_file():mlflow.log_artifact(str(imagen),artifact_path='graficos')
                run_ids.append(run.info.run_id)
                metadata['runs'].append({'nombre':run_name,'run_id':run.info.run_id})
        with mlflow.start_run(run_name='CALIDAD_predicciones_ficticias') as run:
            mlflow.set_tags({**common,'tipo_run':'CALIDAD_FICTICIA','sin_etiquetas_reales':'SI'})
            for fase, step, key in [('base',0,'linea_base_simulada'),('degradacion',1,'degradado_simulado')]:
                datos = quality[key]
                for campo in ('accuracy','precision_macro','recall_macro','f1_macro','falsas_elegibilidades_predichas'):
                    val = datos.get(campo)
                    if numero(val):mlflow.log_metric(campo,float(val),step=step)
                mlflow.log_metric('n_etiquetados_ficticios',int(datos['n_etiquetados']),step=step)
            mlflow.log_metric('alertas_calidad',len(quality.get('alertas',[])))
            mlflow.log_artifact(str(tmp/'metricas/calidad_demo.json'),artifact_path='fuente')
            graph = tmp/'dashboards/calidad_simulada.png'
            if graph.is_file():mlflow.log_artifact(str(graph),artifact_path='graficos')
            metadata['runs'].append({'nombre':'CALIDAD_predicciones_ficticias','run_id':run.info.run_id})
        anti = runs_book.get('antirruido',{})
        alerts = objetos['incidentes/alertas_demo.json']
        with mlflow.start_run(run_name='ALERTAS_SLO_y_runbooks') as run:
            mlflow.set_tags({**common,'tipo_run':'ALERTAS','antirruido':'30_minutos'})
            for campo in ('primera_emision','segunda_emision_2min','suprimidas_2min','emision_31min','cooldown_minutos'):
                if numero(anti.get(campo)):mlflow.log_metric(campo,float(anti[campo]))
            mlflow.log_metric('alertas_generadas',int(alerts.get('generadas',0)))
            # No confundir las alertas del segundo estado con una tasa real de incidentes.
            mlflow.log_metric('alertas_emitidas_estado_reutilizado',len(alerts.get('emitidas',[])))
            mlflow.log_metric('alertas_suprimidas_estado_reutilizado',int(alerts.get('suprimidas',0)))
            log_incs = runs_book.get('incidentes',[])
            mlflow.log_metric('runbooks_registrados',len(log_incs))
            mlflow.log_metric('runbooks_recuperacion_verificada',sum(bool(x.get('recuperacion_verificada')) for x in log_incs))
            for name in ('incidentes/runbooks_ejecutados_demo.json','incidentes/alertas_demo.json','incidentes/metricas_demo.json','incidentes/consola_alertas_demo.txt','dashboards/dashboard_simulado.html'):
                target=tmp/name
                if target.is_file():mlflow.log_artifact(str(target),artifact_path=target.parent.name)
            metadata['runs'].append({'nombre':'ALERTAS_SLO_y_runbooks','run_id':run.info.run_id})

    # Comprobar trazabilidad sin depender de la interfaz grafica.
    client=MlflowClient(tracking_uri=uri)
    encontrados=client.search_runs([experiment.experiment_id],max_results=100)
    encontrados={r.info.run_id for r in encontrados}
    assert all(r['run_id'] in encontrados for r in metadata['runs']), 'No fue posible verificar todos los runs registrados'
    metadata['runs_verificados']=len(metadata['runs'])
    metadata['registrado_utc']=datetime.now(timezone.utc).isoformat()
    salida=tracking_dir/'resumen_registro_mlflow.json'
    salida.write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print('\n=== CIMA A8 | MLflow: SIMULACION OFFLINE ===')
    print('Experimento:',EXPERIMENT)
    print('Tracking:',uri)
    print('SHA256 ZIP:',sha)
    for row in metadata['runs']:print('RUN:',row['nombre'],row['run_id'])
    print('Runs verificados:',metadata['runs_verificados'])
    print('Archivo resumen:',salida)
    return metadata


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path,help='ZIP descargado desde GitHub Actions')
    parser.add_argument('--tracking-dir',type=Path,default=Path('/content/cima_mlflow'))
    parser.add_argument('--workflow-run',default='')
    parser.add_argument('--commit',default='')
    args=parser.parse_args()
    registrar(args.input,args.tracking_dir,args.workflow_run,args.commit)

if __name__=='__main__':main()
