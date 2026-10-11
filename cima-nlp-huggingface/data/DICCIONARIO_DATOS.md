
# Diccionario de datos — CHATBOT CIMA

## Origen del dataset

Dataset sintético diseñado para evaluar modelos preentrenados de
Procesamiento de Lenguaje Natural (NLP).

Los ejemplos fueron construidos considerando la estructura,
nomenclatura y escenarios operativos de la base maestra
Nueva CIE 2.1.

No contiene movimientos bancarios, folios, referencias,
nombres ni importes reales.

## Composición

- Total de registros: 160.
- Categorías: 4.
- Registros por categoría: 40.
- Desarrollo: 20 registros.
- Evaluación: 140 registros.

## Campos

| Campo | Descripción |
|---|---|
| id | Identificador único del ejemplo |
| texto | Solicitud sintética expresada en lenguaje natural |
| clase_real | Clasificación de referencia del ejemplo |
| subtipo | Tipo de operación o escenario representado |
| dificultad | Complejidad estimada de la solicitud |
| particion | Desarrollo o evaluación |
| justificacion | Motivo de asignación de la categoría |

## Categorías

- INDIVIDUAL: consulta de pagos correspondiente a un solo folio.
- PAQUETE: consulta de varios folios o distribución de pagos.
- AMBIGUA: solicitud sin información suficiente para identificar el folio.
- FUERA_ALCANCE: solicitud distinta a la consulta de pagos de venta
  contemplada en el MVP.

## Consideraciones operativas

Un mismo folio puede presentar anticipo, finiquito y
pagos complementarios.

La clasificación INDIVIDUAL identifica el tipo de solicitud,
pero no valida que exista un pago asignado.

Los registros repetidos se conservan en la evaluación original.
Para el diagnóstico se calcularon métricas complementarias
sobre textos únicos.

## Limitaciones

El conjunto está equilibrado artificialmente y no representa
necesariamente la distribución real de solicitudes.

Los resultados no constituyen una validación productiva.
La tercera ejecución es exploratoria porque sus ajustes se
definieron después de observar errores de evaluación.
