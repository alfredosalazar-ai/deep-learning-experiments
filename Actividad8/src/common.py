"""Utilidades compartidas del monitor CIMA. No captura datos bancarios reales."""
from __future__ import annotations
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_config(path: str | Path | None = None) -> dict:
    import yaml
    selected = Path(path) if path else ROOT / "config" / "alerts.yaml"
    data = yaml.safe_load(selected.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "slo" not in data or "alertas" not in data:
        raise ValueError("Configuracion incompleta")
    return data


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def append_jsonl(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def percentile_nearest_rank(values: list[float], p: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    return values[max(0, min(len(values)-1, math.ceil(len(values)*p)-1))]


def public_base(url: str) -> str:
    from urllib.parse import urlparse
    u = urlparse(url)
    if u.scheme not in ("http", "https") or not u.netloc or u.username or u.password:
        raise ValueError("URL base no valida")
    # El monitor solo accede al host indicado y rutas fijas.
    return f"{u.scheme}://{u.netloc}"
