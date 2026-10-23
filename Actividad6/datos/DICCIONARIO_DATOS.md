# Diccionario de datos — Actividad 6 / CHATBOT CIMA

## Fuente y versión

Los datos proceden del dataset sintético `cima_consultas_cie_sinteticas.csv`, utilizado y documentado en la Actividad 5. Los ejemplos reflejan escenarios de consulta de CIMA, pero no contienen movimientos bancarios reales. La base maestra Nueva CIE 2.1 no se incorpora a este repositorio.

## Archivos

- `datos_ini/cima_consultas_original.csv`: 160 registros sintéticos, fuente original de la Actividad 5.
- `datos_limp/cima_consultas_limpias.csv`: 128 textos únicos después de depuración.
- `datos_limp/entrenamiento.csv`: 102 registros para desarrollo y validación.
- `datos_limp/prueba.csv`: 26 registros reservados para evaluación final.
- `datos_limp/resumen_preparacion.json`: metadatos del proceso de preparación de Actividad 5.

## Variables relevantes

| Variable | Descripción | Uso |
|---|---|---|
| `id` | Identificador sintético del ejemplo | Trazabilidad; no es predictor |
| `texto` | Solicitud sintética original | Texto fuente |
| `texto_normalizado` | Solicitud normalizada | Entrada del modelo |
| `clase_real` | Etiqueta objetivo | `INDIVIDUAL`, `PAQUETE`, `AMBIGUA`, `FUERA_ALCANCE` |
| `subtipo` | Escenario de consulta | Metadato; no predictor |
| `dificultad` | Dificultad asignada al ejemplo | Metadato; no predictor |
| `particion_a5` | Entrenamiento o prueba | Reutilizada para mantener el protocolo A5 |
| `version_dataset` | Versión del conjunto depurado | Control de versión |

## Supuestos y limitaciones

La prueba contiene 26 consultas: ocho `INDIVIDUAL`, ocho `PAQUETE`, dos `AMBIGUA` y ocho `FUERA_ALCANCE`. La clase `AMBIGUA` tiene muy pocos ejemplos para estimar de forma estable el desempeño. Los resultados se interpretan como una evaluación exploratoria, no como evidencia de desempeño productivo.
