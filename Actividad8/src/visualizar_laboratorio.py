"""Genera gráficas PNG estáticas a partir de la evidencia sintética exportada."""
from __future__ import annotations
from pathlib import Path
from .common import ROOT,load_json


def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    folder=ROOT/'results'/'dashboards'
    folder.mkdir(parents=True,exist_ok=True)
    report=load_json(ROOT/'results'/'incidentes'/'runbooks_ejecutados_demo.json')
    if not report or report.get('origen')!='SIMULACION_OFFLINE':
        raise ValueError('Ejecutar python -m src.laboratorio para generar la evidencia sintética')
    items=report['incidentes']
    names=['Latencia P95\n(ms)','PSI\ndrift','Errores 5xx\n(%)']
    keys=['latencia_p95_ms','drift_psi','error_5xx_rate']
    factors=[1,1,100]
    import math
    # Tres paneles separados, no comparten unidades
    for item,name,key,factor in zip(items,names,keys,factors):
        values=[item[stage].get(key,0)*factor for stage in ('metricas_antes','metricas_durante','metricas_despues')]
        fig,ax=plt.subplots(figsize=(6.4,3.4))
        bars=ax.bar(['Antes','Durante','Después'],values)
        ax.set_ylabel(name.replace('\n',' '))
        ax.set_title(f"{item['incidente']} · antes / durante / después (simulado)")
        ax.set_ylim(0,max(values)*1.24 if max(values) else 1)
        for bar,value in zip(bars,values):
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height(),f'{value:.2f}',ha='center',va='bottom',fontsize=9)
        fig.tight_layout()
        fig.savefig(folder/f"{item['incidente']}_indicador.png",dpi=150)
        plt.close(fig)
    q=report['calidad']
    fig,ax=plt.subplots(figsize=(6.4,3.5))
    categories=['Accuracy','F1 macro']
    base=[q['linea_base_simulada']['accuracy'],q['linea_base_simulada']['f1_macro']]
    after=[q['degradado_simulado']['accuracy'],q['degradado_simulado']['f1_macro']]
    x=[0,1]
    ax.bar([v-.18 for v in x],base,width=.36,label='Base simulada')
    ax.bar([v+.18 for v in x],after,width=.36,label='Degradación simulada')
    ax.set_ylim(0,1.08)
    ax.set_xticks(x,categories)
    ax.set_title('Calidad predictiva · datos ficticios del laboratorio')
    ax.legend()
    fig.tight_layout()
    fig.savefig(folder/'calidad_simulada.png',dpi=150)
    plt.close(fig)
    print('Gráficas sintéticas guardadas en',folder)

if __name__=='__main__':main()
