"""
standards.py
Loads and validates water quality standards from config/standards/*.json
Supports pluggable multi-standard architecture.
"""

import json
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Optional

STANDARDS_DIR = Path(__file__).resolve().parents[2] / "config" / "standards"


class ParameterSpec(BaseModel):
    ideal: float
    permissible: list[float]   # [min, max]
    unit: str
    weight: float


class WaterStandard(BaseModel):
    standard: str
    region: str
    parameters: Dict[str, ParameterSpec]


def load_standard(name: str) -> WaterStandard:
    """Load a standard by name (e.g. 'bis', 'who')."""
    path = STANDARDS_DIR / f"{name.lower()}.json"
    if not path.exists():
        raise FileNotFoundError(f"Standard '{name}' not found at {path}")
    with open(path) as f:
        data = json.load(f)
    return WaterStandard(**data)


def list_standards() -> list[str]:
    """Return all available standard names."""
    return [p.stem for p in STANDARDS_DIR.glob("*.json")]
