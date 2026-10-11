
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]

"""
CHATBOT CIMA - Actividad 4
Validacion del dataset sintetico basado en la estructura CIE.

Este script verifica integridad, distribucion y consistencia.
No modifica ni elimina registros.

Ejecucion desde la raiz del proyecto:
    python src/validar_dataset.py
"""

from pathlib import Path
import sys

import pandas as pd


# Rutas relativas al proyecto
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "cima_consultas_cie_sinteticas.csv"
)

REQUIRED_COLUMNS = [
    "id",
    "texto",
    "clase_real",
    "subtipo",
    "dificultad",
    "particion",
    "justificacion",
]

CLASSES = [
    "INDIVIDUAL",
    "PAQUETE",
    "AMBIGUA",
    "FUERA_ALCANCE",
]

EXPECTED_PARTITIONS = {
    "desarrollo": 20,
    "evaluacion": 140,
}


def validar_dataset():
    print("=" * 60)
    print("CHATBOT CIMA - VALIDACION DEL DATASET")
    print("=" * 60)

    # 1. Existencia del archivo
    if not DATA_PATH.is_file():
        raise FileNotFoundError(
            f"No se encontro el dataset: {DATA_PATH}"
        )

    # 2. Lectura
    df = pd.read_csv(
        DATA_PATH,
        encoding="utf-8-sig",
        dtype={"id": str, "texto": str},
    )

    errores = []
    advertencias = []

    # 3. Columnas obligatorias
    faltantes = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if faltantes:
        raise ValueError(
            f"Faltan columnas obligatorias: {faltantes}"
        )

    # 4. Cantidad de registros
    if len(df) != 160:
        errores.append(
            f"Se esperaban 160 registros; encontrados: {len(df)}"
        )

    # 5. Identificadores
    if df["id"].isna().any():
        errores.append("Existen identificadores vacios.")

    if df["id"].duplicated().any():
        errores.append("Existen identificadores duplicados.")

    # 6. Textos
    if df["texto"].isna().any():
        errores.append("Existen consultas sin texto.")

    if df["texto"].fillna("").str.strip().eq("").any():
        errores.append("Existen consultas vacias.")

    # 7. Valores obligatorios
    for campo in REQUIRED_COLUMNS:
        if df[campo].isna().any():
            errores.append(
                f"El campo {campo} contiene valores nulos."
            )

    # 8. Categorias
    clases_encontradas = set(df["clase_real"].dropna())

    if clases_encontradas != set(CLASSES):
        errores.append(
            f"Categorias inesperadas: {clases_encontradas}"
        )

    conteo_clases = (
        df["clase_real"]
        .value_counts()
        .reindex(CLASSES, fill_value=0)
    )

    if not conteo_clases.eq(40).all():
        errores.append(
            "Cada categoria debe contener 40 registros."
        )

    # 9. Particiones
    particiones = df["particion"].value_counts().to_dict()

    if particiones != EXPECTED_PARTITIONS:
        errores.append(
            f"Distribucion incorrecta: {particiones}"
        )

    # 10. Repeticiones de texto
    duplicados = int(df["texto"].duplicated().sum())

    if duplicados > 0:
        advertencias.append(
            f"Se identificaron {duplicados} textos repetidos. "
            "Se conservan para reproducir la evaluacion original."
        )

    # 11. Etiquetas contradictorias
    conflictos = (
        df.groupby("texto")["clase_real"]
        .nunique()
    )

    textos_conflictivos = int((conflictos > 1).sum())

    if textos_conflictivos:
        errores.append(
            f"{textos_conflictivos} textos tienen "
            "etiquetas contradictorias."
        )

    # 12. Posible repeticion entre particiones
    desarrollo = set(
        df.loc[
            df["particion"] == "desarrollo", "texto"
        ]
    )

    evaluacion = set(
        df.loc[
            df["particion"] == "evaluacion", "texto"
        ]
    )

    compartidos = desarrollo.intersection(evaluacion)

    if compartidos:
        advertencias.append(
            f"{len(compartidos)} textos aparecen tanto en "
            "desarrollo como en evaluacion."
        )

    # 13. Resumen
    print(f"\nArchivo: {DATA_PATH.name}")
    print(f"Total de registros: {len(df)}")

    print("\nDistribucion por categoria:")
    print(conteo_clases.to_string())

    print("\nDistribucion por particion:")
    print(
        pd.crosstab(
            df["clase_real"],
            df["particion"]
        ).to_string()
    )

    print(f"\nTextos repetidos: {duplicados}")
    print(f"Textos con etiquetas contradictorias: "
          f"{textos_conflictivos}")

    # 14. Advertencias
    if advertencias:
        print("\nADVERTENCIAS:")
        for mensaje in advertencias:
            print(f"- {mensaje}")

    # 15. Resultado final
    if errores:
        print("\nVALIDACION NO SUPERADA:")
        for mensaje in errores:
            print(f"- {mensaje}")
        return False

    print("\nVALIDACION ESTRUCTURAL SUPERADA.")
    print(
        "El dataset mantiene la estructura requerida "
        "para reproducir el experimento."
    )

    return True


if __name__ == "__main__":
    try:
        resultado = validar_dataset()
        sys.exit(0 if resultado else 1)
    except (FileNotFoundError, ValueError) as exc:
        print(f"\nERROR: {exc}")
        sys.exit(1)
