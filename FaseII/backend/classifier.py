"""Carga y ejecuta el pipeline NLP entrenado de CIMA."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import joblib

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT / "modelos" / "Regresion_Logistica.joblib"
CLASSES = {"INDIVIDUAL", "PAQUETE", "AMBIGUA", "FUERA_ALCANCE"}
DEFAULT_THRESHOLD = 0.276334  # Valor consolidado en Actividad 6; configurable por entorno.


class CIMAClassifier:
    """Adaptador seguro del modelo; no autoriza pagos ni ejecuta operaciones."""

    def __init__(self, model_path: str | Path | None = None, threshold: float | None = None):
        self.model_path = Path(model_path or os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
        raw_threshold = threshold if threshold is not None else os.getenv(
            "INDIVIDUAL_THRESHOLD", str(DEFAULT_THRESHOLD)
        )
        try:
            self.threshold = float(raw_threshold)
        except (TypeError, ValueError) as exc:
            raise ValueError("INDIVIDUAL_THRESHOLD debe ser numérico.") from exc
        if not 0 <= self.threshold <= 1:
            raise ValueError("INDIVIDUAL_THRESHOLD debe estar entre 0 y 1.")
        if not self.model_path.is_file():
            raise FileNotFoundError(f"No se encontró el modelo: {self.model_path}")
        self.model: Any = joblib.load(self.model_path)
        model_classes = {str(c) for c in getattr(self.model, "classes_", [])}
        if not CLASSES.issubset(model_classes):
            raise ValueError(
                f"El modelo no contiene todas las clases esperadas: {sorted(CLASSES)}"
            )
        if not hasattr(self.model, "predict_proba"):
            raise ValueError("El modelo debe exponer predict_proba para esta política de umbral.")

    def predict(self, texto: str) -> dict[str, object]:
        """Clasifica un texto y aplica una política de aceptación selectiva."""
        predicted = str(self.model.predict([texto])[0])
        classes = [str(c) for c in self.model.classes_]
        individual_index = classes.index("INDIVIDUAL")
        score = float(self.model.predict_proba([texto])[0][individual_index])

        # La consulta avanza al flujo individual solo si coinciden la clase y el umbral.
        accepted = predicted == "INDIVIDUAL" and score >= self.threshold
        decision = "APTO_PARA_FLUJO_INDIVIDUAL" if accepted else "REVISION_HUMANA"
        return {
            "clase_predicha": predicted,
            "decision_operativa": decision,
            "requiere_revision_humana": not accepted,
            "puntaje_individual": score,
            "umbral_individual": self.threshold,
            "version_modelo": "actividad5-regresion-logistica-a5-v1.0",
            "advertencia": (
                "La clasificación es apoyo informativo; no autoriza pagos ni sustituye "
                "validaciones deterministas o revisión humana cuando corresponda."
            ),
        }
