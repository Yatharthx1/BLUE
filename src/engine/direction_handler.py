"""
direction_handler.py

Given a measured value and a param's limits + direction,
computes the raw geometry of deviation.

Output: DirectionResult(distance, side, normalized_distance)

  distance            : raw gap from nearest ideal boundary
  side                : "in_range" | "high" | "low"
  normalized_distance : distance / total_range  (0.0 = perfect, 1.0 = at limit edge)
                        ML-ready, cross-param comparable
"""

from dataclasses import dataclass
from typing import Literal


Side = Literal["in_range", "high", "low"]


@dataclass
class DirectionResult:
    distance:            float
    side:                Side
    normalized_distance: float


class DirectionHandler:

    def compute(self, value: float, direction: str, limits: dict) -> DirectionResult:
        """
        Route to the correct geometry based on direction.

        direction: "up_bad" | "down_bad" | "both_bad"
        limits:    the limits dict from the profile param
        """
        if direction == "up_bad":
            return self._up_bad(value, limits)
        elif direction == "down_bad":
            return self._down_bad(value, limits)
        elif direction == "both_bad":
            return self._both_bad(value, limits)
        else:
            raise ValueError(f"Unknown direction: '{direction}'")

    # ── up_bad ────────────────────────────────────────────────────────────────
    # Lower is better. Ideal = 0 (or ideal scalar). Bad as value rises.

    def _up_bad(self, value: float, limits: dict) -> DirectionResult:
        ideal      = limits.get("ideal", 0)
        acceptable = limits["acceptable"]  # scalar upper bound

        # Total reference range for normalization
        permissible = limits.get("permissible", acceptable)
        total_range = permissible - ideal if permissible != ideal else acceptable

        if value <= ideal:
            return DirectionResult(distance=0.0, side="in_range", normalized_distance=0.0)

        distance = value - ideal
        norm     = distance / total_range if total_range > 0 else 1.0
        side     = "high"
        return DirectionResult(distance=round(distance, 6), side=side,
                               normalized_distance=round(min(norm, 2.0), 6))

    # ── down_bad ──────────────────────────────────────────────────────────────
    # Higher is better. Ideal at top. Bad as value falls.

    def _down_bad(self, value: float, limits: dict) -> DirectionResult:
        ideal       = limits["ideal"]          # scalar upper ideal (e.g. 14.6 for DO)
        acceptable  = limits["acceptable"]     # lower acceptable threshold
        permissible = limits.get("permissible", acceptable)  # lower permissible threshold
        total_range = ideal - permissible if ideal != permissible else ideal - acceptable

        if value >= ideal:
            return DirectionResult(distance=0.0, side="in_range", normalized_distance=0.0)

        distance = ideal - value
        norm     = distance / total_range if total_range > 0 else 1.0
        return DirectionResult(distance=round(distance, 6), side="low",
                               normalized_distance=round(min(norm, 2.0), 6))

    # ── both_bad ──────────────────────────────────────────────────────────────
    # Ideal is a range. Bad in either direction (pH, TDS, fluoride).

    def _both_bad(self, value: float, limits: dict) -> DirectionResult:
        acceptable = limits["acceptable"]  # [lo, hi]
        acc_lo, acc_hi = acceptable

        # Ideal range (fallback to acceptable if not specified)
        ideal = limits.get("ideal", acceptable)
        if isinstance(ideal, list):
            ideal_lo, ideal_hi = ideal
        else:
            ideal_lo = ideal_hi = ideal  # scalar ideal treated as point

        permissible = limits.get("permissible")
        # For normalization: max possible range from ideal center
        center      = (ideal_lo + ideal_hi) / 2
        ref_hi      = permissible if permissible else acc_hi
        total_range = max(ref_hi - center, center - acc_lo, 1.0)

        # In ideal zone
        if ideal_lo <= value <= ideal_hi:
            return DirectionResult(distance=0.0, side="in_range", normalized_distance=0.0)

        if value > ideal_hi:
            distance = value - ideal_hi
            side     = "high"
        else:
            distance = ideal_lo - value
            side     = "low"

        norm = distance / total_range
        return DirectionResult(distance=round(distance, 6), side=side,
                               normalized_distance=round(min(norm, 2.0), 6))
