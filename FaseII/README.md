# Fase II — Ejecución de CHATBOT CIMA

Prototipo desplegable de clasificación de consultas CIMA mediante FastAPI, un pipeline NLP entrenado en la Actividad 5 y una interfaz web ligera. El proyecto se construye y prueba en GitHub Actions y está preparado para desplegarse desde su `Dockerfile` en Render, sin instalar Docker en la computadora del estudiante.

## Arquitectura

- **Frontend:** HTML, CSS y JavaScript servido por FastAPI.
- **Backend:** API REST con FastAPI.
- **Modelo:** `modelos/Regresion_Logistica.joblib`, pipeline TF-IDF + Regresión Logística de la Actividad 5.
- **Contenedor:** `Dockerfile` basado en `python:3.12-slim`.
- **CI remota:** `.github/workflows/fase2-docker.yml` en la raíz del repositorio; ejecuta pruebas y construye/prueba la imagen en un runner alojado por GitHub.

## Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| `GET` | `/` | Interfaz web |
| `GET` | `/health` | Estado de API y carga del modelo |
| `POST` | `/predict` | Clasificación de una consulta |
| `GET` | `/docs` | Documentación Swagger/OpenAPI |

Ejemplo de petición:

```json
{
  "texto": "Solicito confirmar el pago asociado al folio 12345."
}
```

La respuesta contiene la clase predicha, el puntaje estimado para `INDIVIDUAL`, el umbral, una decisión de enrutamiento y una advertencia operativa. La política acepta el flujo individual solo cuando la clase predicha es `INDIVIDUAL` y el puntaje supera `INDIVIDUAL_THRESHOLD` (valor experimental consolidado: `0.276334`). Los demás casos se envían a `REVISION_HUMANA`.

## Seguridad y alcance

- Prototipo académico que utiliza datos/modelos sintéticos y no transacciones reales.
- Una predicción **no confirma transacciones ni autoriza pagos**.
- El servicio no cuenta con autenticación ni controles empresariales; no exponerlo como sistema productivo ni introducir información confidencial.
- Solo cargar artefactos `joblib` procedentes de este repositorio confiable; deserializar artefactos manipulados puede ejecutar código.
- El umbral proviene de la evaluación de Actividad 6 y necesita reevaluación con datos nuevos antes de cualquier uso operativo.

## Publicar en el repositorio

La carpeta debe quedar en la raíz del repositorio como `FaseII/`. El workflow debe publicarse además en `.github/workflows/fase2-docker.yml` (la carpeta `.github` va en la raíz del repositorio, no dentro de `FaseII`). Tras hacer commit, abre **Actions** y confirma que el workflow termine en verde.

## Despliegue en Render

1. Publica `FaseII/` en la rama `main` del repositorio.
2. En Render crea un **Web Service** y conecta el repositorio.
3. Selecciona runtime **Docker**.
4. Configura la raíz/directorio del servicio a `FaseII` o, si el formulario solicita rutas desde la raíz del repositorio, especifica `FaseII/Dockerfile` y el contexto `FaseII`.
5. No sobrescribas el comando Docker salvo que sea necesario; el contenedor escucha en la variable `PORT` del proveedor (o puerto 8000 por defecto).
6. Configura Health Check Path como `/health` si la opción está disponible.
7. Una vez desplegado, comprueba `https://<tu-servicio>.onrender.com/`, `/health` y `/docs`, y ejecuta una solicitud de prueba en `/docs`.
8. Captura las evidencias de construcción, despliegue y prueba funcional; documenta el resultado real, no uno supuesto.

## Pruebas automatizadas

El workflow ejecuta `pytest -q`, construye la imagen Docker y comprueba el endpoint `/health` y una inferencia HTTP dentro del contenedor.

## Archivos principales

- `backend/main.py`: rutas API y health check.
- `backend/classifier.py`: carga del pipeline y política de umbral.
- `backend/schemas.py`: validación de entradas y respuesta.
- `frontend/`: interfaz web.
- `tests/test_api.py`: pruebas funcionales y casos de entrada inválida.
- `requirements.txt`: dependencias fijadas.
- `Dockerfile`: construcción de la imagen.
