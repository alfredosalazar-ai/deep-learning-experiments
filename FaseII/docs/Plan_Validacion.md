# Plan de validación y pruebas — Fase II

## Objetivo
Verificar la integración entre la interfaz web, la API FastAPI y el pipeline NLP empaquetado en el contenedor Docker.

## Casos automatizados

| ID | Prueba | Resultado esperado |
|---|---|---|
| T01 | Abrir `/` | HTTP 200 y se muestra CHATBOT CIMA |
| T02 | Consultar `/health` | HTTP 200, `status=ok`, `model_loaded=true` |
| T03 | Enviar texto válido a `/predict` | HTTP 200, etiqueta válida y decisión de enrutamiento |
| T04 | Enviar solo espacios | HTTP 422 |
| T05 | Omitir `texto` | HTTP 422 |
| T06 | Texto de más de 5,000 caracteres | HTTP 422 |
| T07 | Consultar `/openapi.json` | HTTP 200 y ruta `/predict` documentada |
| T08 | Construir y ejecutar imagen Docker en CI | Construcción exitosa, `/health` e inferencia responden |

## Resultados
Los resultados deberán completarse a partir de la ejecución real de GitHub Actions y del despliegue en Render. No registrar estos casos como aprobados hasta contar con evidencia.

## Límites
La API devuelve una clasificación experimental. No valida el folio contra sistemas maestros, no comprueba estados de pago y no autoriza transacciones. La prueba de software no sustituye una validación de negocio ni una evaluación con consultas operativas independientes.
