"""API HTTP y frontend mínimo de CHATBOT CIMA."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.classifier import CIMAClassifier
from backend.schemas import PredictionRequest, PredictionResponse

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("cima-api")
APP_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = APP_ROOT / "frontend"

classifier: CIMAClassifier | None = None


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Carga el modelo al iniciar y registra fallas de manera verificable."""
    global classifier
    try:
        classifier = CIMAClassifier()
        logger.info("Modelo de CIMA cargado desde %s", classifier.model_path)
    except Exception:
        logger.exception("No fue posible cargar el modelo de CIMA")
        classifier = None
    yield


app = FastAPI(
    title="CHATBOT CIMA — API de clasificación",
    description=(
        "Prototipo académico para clasificar consultas operativas sintéticas. "
        "La predicción no autoriza pagos ni sustituye los controles operativos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    """Entrega la interfaz web ligera."""
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health", tags=["operación"])
def health() -> dict[str, object]:
    """Health check para CI y el proveedor de nube."""
    return {
        "status": "ok" if classifier is not None else "degraded",
        "model_loaded": classifier is not None,
        "service": "cima-api",
    }


@app.post("/predict", response_model=PredictionResponse, tags=["clasificación"])
def predict(request: PredictionRequest) -> PredictionResponse:
    """Clasifica texto y devuelve clase, puntaje y decisión de enrutamiento."""
    if classifier is None:
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible; revisar el registro del servicio.",
        )
    try:
        result = classifier.predict(request.texto)
        return PredictionResponse(**result)
    except Exception as exc:
        logger.exception("Error durante la inferencia")
        raise HTTPException(status_code=500, detail="No fue posible procesar la consulta.") from exc
