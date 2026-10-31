"""Esquemas de entrada y salida de la API."""
from pydantic import BaseModel, Field, field_validator


class PredictionRequest(BaseModel):
    """Consulta de texto que se desea clasificar."""

    texto: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Texto de la consulta CIMA (máximo 5,000 caracteres).",
        examples=["Solicito confirmar el pago asociado al folio 12345."],
    )

    @field_validator("texto")
    @classmethod
    def texto_no_vacio(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El texto no puede estar vacío ni contener solo espacios.")
        return value


class PredictionResponse(BaseModel):
    """Respuesta de clasificación y enrutamiento seguro."""

    clase_predicha: str
    decision_operativa: str
    requiere_revision_humana: bool
    puntaje_individual: float | None = None
    umbral_individual: float
    version_modelo: str
    advertencia: str
