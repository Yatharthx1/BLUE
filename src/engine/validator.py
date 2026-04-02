"""
validator.py

Validates a raw input value before scoring.
Returns a ValidationResult — engine only scores if valid=True.

Confidence = valid_params / total_expected_params
So skipping params due to missing/invalid data penalizes confidence,
preventing artificially inflated WQI scores.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ValidationResult:
    valid:      bool
    flag_code:  Optional[str]   # "NO_DATA" | "INVALID" | "SUSPECT" | None
    message:    Optional[str]
    contributes_to_confidence: bool = True


class ParameterValidator:

    def validate(self, param: str, value, spec: dict) -> ValidationResult:
        """
        Run all checks in order. First failure wins.
        """
        # ── Missing / None ────────────────────────────────────────────────────
        if value is None:
            return ValidationResult(
                valid=False,
                flag_code="NO_DATA",
                message=f"{param}: value is missing",
                contributes_to_confidence=True   # still counts against confidence
            )

        # ── Non-numeric ───────────────────────────────────────────────────────
        try:
            value = float(value)
        except (TypeError, ValueError):
            return ValidationResult(
                valid=False,
                flag_code="INVALID",
                message=f"{param}: non-numeric value '{value}'",
                contributes_to_confidence=True
            )

        # ── Physically impossible (negative where impossible) ─────────────────
        non_negative_params = {
            "TDS", "turbidity", "hardness", "nitrates", "arsenic",
            "lead", "coliform", "BOD", "chlorides", "dissolved_oxygen", "fluoride"
        }
        if param in non_negative_params and value < 0:
            return ValidationResult(
                valid=False,
                flag_code="INVALID",
                message=f"{param}: negative value {value} is physically impossible",
                contributes_to_confidence=True
            )

        # ── Suspect: extreme outlier (> 10x the permissible / acceptable) ─────
        limits   = spec.get("limits", {})
        ceiling  = limits.get("permissible") or limits.get("acceptable")
        if ceiling:
            if isinstance(ceiling, list):
                ceiling = ceiling[1]
            if isinstance(ceiling, (int, float)) and ceiling > 0 and value > ceiling * 10:
                return ValidationResult(
                    valid=False,
                    flag_code="SUSPECT",
                    message=f"{param}: value {value} is >10x the limit ({ceiling}), likely a unit error",
                    contributes_to_confidence=True
                )

        return ValidationResult(valid=True, flag_code=None, message=None)
