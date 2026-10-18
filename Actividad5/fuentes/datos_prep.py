"""Preparacion reproducible del dataset NLP sintetico de CIMA (Actividad 5).

Ejecutar desde cualquier directorio: python Actividad5/fuentes/datos_prep.py
Mantiene intacto el CSV original, elimina textos IDENTICOS normalizados
solo para clasificacion de intencion, y divide train/test sin solapamientos.
No altera los registros contables de Nueva CIE 2.1.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'datos' / 'datos_ini' / 'cima_consultas_original.csv'
OUT = ROOT / 'datos' / 'datos_limp'
FIGS = ROOT / 'resultados'
CLASSES = ['INDIVIDUAL', 'PAQUETE', 'AMBIGUA', 'FUERA_ALCANCE']
SEED = 20261015


def normalizar_texto(texto: str) -> str:
    """Solo NFKC y espacios: conserva tildes, numeros y semantica."""
    texto = unicodedata.normalize('NFKC', str(texto))
    return re.sub(r'\s+', ' ', texto).strip()


def clave_duplicado(texto: str) -> str:
    """Clave de equivalencia textual, sin eliminar acentos ni puntuacion."""
    return normalizar_texto(texto).casefold()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def preparar() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    FIGS.mkdir(parents=True, exist_ok=True)
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    df = pd.read_csv(SOURCE, encoding='utf-8-sig', dtype=str, keep_default_na=False)
    required = ['id', 'texto', 'clase_real', 'subtipo', 'dificultad', 'particion', 'justificacion']
    if any(c not in df.columns for c in required):
        raise ValueError(f'Faltan columnas: {set(required) - set(df.columns)}')
    if len(df) != 160 or df['id'].duplicated().any():
        raise ValueError('Se esperaban 160 registros con ID unico')
    if not set(df['clase_real']).issubset(set(CLASSES)):
        raise ValueError('Etiquetas no reconocidas')
    if df['texto'].map(normalizar_texto).eq('').any():
        raise ValueError('Textos vacios')

    df['texto_normalizado'] = df['texto'].map(normalizar_texto)
    df['_clave'] = df['texto_normalizado'].map(clave_duplicado)
    contradicciones = df.groupby('_clave')['clase_real'].nunique()
    if (contradicciones > 1).any():
        raise ValueError('Hay textos iguales con etiquetas distintas; resolver manualmente')

    # Auditar posibles solapamientos de la particion previa de zero-shot.
    inter = (set(df.loc[df.particion == 'desarrollo', '_clave']) &
             set(df.loc[df.particion == 'evaluacion', '_clave']))
    original_counts = df['clase_real'].value_counts().reindex(CLASSES, fill_value=0)
    # Para NLP un texto identico no aporta informacion de intencion nueva.
    # Se conserva la primera fila, sin reescribir el dato original.
    limpio = df.drop_duplicates('_clave', keep='first').copy()
    duplicados_retirados = len(df) - len(limpio)

    # Estratificacion sobre textos UNICOS, no particiones de Actividad 4.
    train_idx, test_idx = train_test_split(
        limpio.index, test_size=0.20, random_state=SEED,
        stratify=limpio['clase_real']
    )
    limpio['particion_a5'] = 'entrenamiento'
    limpio.loc[test_idx, 'particion_a5'] = 'prueba'
    limpio['version_dataset'] = 'a5-v1.0'
    limpio = limpio.drop(columns=['_clave']).sort_values('id').reset_index(drop=True)
    # Conservar campos de origen y la columna de texto normalizada, sin alterar etiquetas.
    clean_path = OUT / 'cima_consultas_limpias.csv'
    train_path = OUT / 'entrenamiento.csv'
    test_path = OUT / 'prueba.csv'
    limpio.to_csv(clean_path, index=False, encoding='utf-8-sig')
    limpio.loc[limpio.particion_a5 == 'entrenamiento'].to_csv(train_path, index=False, encoding='utf-8-sig')
    limpio.loc[limpio.particion_a5 == 'prueba'].to_csv(test_path, index=False, encoding='utf-8-sig')

    counts = limpio['clase_real'].value_counts().reindex(CLASSES, fill_value=0)
    ct = pd.crosstab(limpio.clase_real, limpio.particion_a5).reindex(CLASSES, fill_value=0)
    if set(limpio.loc[limpio.particion_a5 == 'entrenamiento', 'texto_normalizado'].map(clave_duplicado)) & set(limpio.loc[limpio.particion_a5 == 'prueba', 'texto_normalizado'].map(clave_duplicado)):
        raise AssertionError('Fuga de texto entre train/test')

    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = range(len(CLASSES))
    ax.bar([i-0.18 for i in x], original_counts.to_numpy(), width=.36, label='Original')
    ax.bar([i+0.18 for i in x], counts.to_numpy(), width=.36, label='Limpio (textos unicos)')
    ax.set_xticks(list(x), CLASSES, rotation=15)
    ax.set_title('CIMA A5 - Impacto de la deduplicacion por clase')
    ax.set_ylabel('Consultas')
    ax.legend(); fig.tight_layout()
    fig.savefig(FIGS / '01_antes_despues_duplicados.png', dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ct[['entrenamiento', 'prueba']].plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('CIMA A5 - Particion de textos unicos')
    ax.set_ylabel('Consultas')
    ax.set_xlabel('Clase real')
    ax.tick_params(axis='x', rotation=15)
    fig.tight_layout()
    fig.savefig(FIGS / '02_particiones_clases.png', dpi=160)
    plt.close(fig)

    summary = {
        'version_dataset': 'a5-v1.0', 'semilla': SEED,
        'fuente': 'Dataset sintetico CIMA publicado en Actividad 4; no es la base operativa CIE',
        'registros_originales': int(len(df)),
        'registros_limpios': int(len(limpio)),
        'duplicados_exactos_normalizados_retirados': int(duplicados_retirados),
        'textos_compartidos_particion_anterior': int(len(inter)),
        'etiquetas_contradictorias': 0,
        'conteo_original_por_clase': {k: int(v) for k, v in original_counts.items()},
        'conteo_limpio_por_clase': {k: int(v) for k, v in counts.items()},
        'particion': {k: {j: int(v) for j, v in d.items()} for k, d in ct.to_dict('index').items()},
        'regla_limpieza': 'Unicode NFKC, espacios, deduplicacion de texto tras casefold; sin stem, lemmatizacion ni quitar acentos',
        'particion_original_a4_no_reutilizada': True,
        'original_sha256': sha256(SOURCE),
        'limpio_sha256': sha256(clean_path),
        'limitaciones': ['Sintetico: no representa distribucion de produccion', 'Solo 10 formulaciones unicas AMBIGUA antes de particionar', 'Dividir por texto evita fuga exacta pero no garantiza independencia semantica de plantillas']
    }
    (OUT / 'resumen_preparacion.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Datos originales:', len(df), ' / limpios:', len(limpio))
    print('Duplicados retirados:', duplicados_retirados)
    print('Textos repetidos entre particiones anteriores:', len(inter))
    print('Clases limpias:\n', counts.to_string())
    print('Train/test:\n', ct.to_string())
    print('SHA256 original:', summary['original_sha256'])
    print('SHA256 limpio:', summary['limpio_sha256'])
    return summary


if __name__ == '__main__':
    preparar()
