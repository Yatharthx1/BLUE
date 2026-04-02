"""
zone_mapper.py

Given a DirectionResult + param spec, maps deviation to:
  zone : "ideal" | "acceptable" | "permissible" | "breach" | "deficient"
  qi   : float  (0 = perfect, 100 = at outer limit, >100 = breach)

Zone → qi mapping:
  ideal       → 0
  acceptable  → 0  to  50   (linear)
  permissible → 50 to  100  (linear)
  breach      → 100+        (linear extrapolation, unbounded)
  deficient   → mirrors acceptable/permissible but on low side

This file knows nothing about param names.
It only reads limits + direction result.
"""

from dataclasses import dataclass
from .direction_handler import DirectionResult


@dataclass
class ZoneResult:
    qi:   float
    zone: str


def _linear(value: float, lo: float, hi: float, qi_lo: float, qi_hi: float) -> float:
    """Map value in [lo, hi] linearly onto [qi_lo, qi_hi]."""
    if hi == lo:
        return qi_lo
    return qi_lo + (qi_hi - qi_lo) * (value - lo) / (hi - lo)


class ZoneMapper:

    def map(self, value: float, dr: DirectionResult,
            direction: str, limits: dict, relaxable: bool) -> ZoneResult:
        """
        Route to correct zone logic based on direction.
        """
        if dr.side == "in_range":
            return ZoneResult(qi=0.0, zone="ideal")

        if direction == "up_bad":
            return self._map_up(value, limits, relaxable)
        elif direction == "down_bad":
            return self._map_down(value, limits, relaxable)
        elif direction == "both_bad":
            return self._map_both(value, dr, limits, relaxable)
        else:
            raise ValueError(f"Unknown direction: '{direction}'")

    # ── up_bad ────────────────────────────────────────────────────────────────

    def _map_up(self, value: float, limits: dict, relaxable: bool) -> ZoneResult:
        ideal       = limits.get("ideal", 0)
        acceptable  = limits["acceptable"]
        permissible = limits.get("permissible") if relaxable else None

        if value <= ideal:
            return ZoneResult(qi=0.0, zone="ideal")

        if value <= acceptable:
            qi = _linear(value, ideal, acceptable, 0, 50)
            return ZoneResult(qi=round(qi, 4), zone="acceptable")

        if permissible and value <= permissible:
            qi = _linear(value, acceptable, permissible, 50, 100)
            return ZoneResult(qi=round(qi, 4), zone="permissible")

        # Breach
        ref = permissible if permissible else acceptable
        qi  = 100 + _linear(value - ref, 0, ref, 0, 100) if ref > 0 else 200
        return ZoneResult(qi=round(min(qi, 300), 4), zone="breach")

    # ── down_bad ──────────────────────────────────────────────────────────────

    def _map_down(self, value: float, limits: dict, relaxable: bool) -> ZoneResult:
        ideal       = limits["ideal"]
        acceptable  = limits["acceptable"]   # lower acceptable bound
        permissible = limits.get("permissible") if relaxable else None  # lower permissible bound

        if value >= ideal:
            return ZoneResult(qi=0.0, zone="ideal")

        if value >= acceptable:
            qi = _linear(value, ideal, acceptable, 0, 50)
            return ZoneResult(qi=round(qi, 4), zone="acceptable")

        if permissible and value >= permissible:
            qi = _linear(value, acceptable, permissible, 50, 100)
            return ZoneResult(qi=round(qi, 4), zone="permissible")

        # Breach (value fell below permissible floor)
        ref = permissible if permissible else acceptable
        qi  = 100 + (ref - value) / ref * 100 if ref > 0 else 200
        return ZoneResult(qi=round(min(qi, 300), 4), zone="breach")

    # ── both_bad ──────────────────────────────────────────────────────────────

    def _map_both(self, value: float, dr: DirectionResult,
                  limits: dict, relaxable: bool) -> ZoneResult:

        acceptable = limits["acceptable"]    # [lo, hi]
        acc_lo, acc_hi = acceptable

        ideal = limits.get("ideal", acceptable)
        if isinstance(ideal, list):
            ideal_lo, ideal_hi = ideal
        else:
            ideal_lo = ideal_hi = ideal

        permissible = limits.get("permissible") if relaxable else None

        # ── High side ────────────────────────────────────────
        if dr.side == "high":
            if value <= acc_hi:
                qi = _linear(value, ideal_hi, acc_hi, 0, 50)
                return ZoneResult(qi=round(qi, 4), zone="acceptable")
            if permissible and value <= permissible:
                qi = _linear(value, acc_hi, permissible, 50, 100)
                return ZoneResult(qi=round(qi, 4), zone="permissible")
            ref = permissible if permissible else acc_hi
            qi  = 100 + (value - ref) / ref * 100 if ref > 0 else 200
            return ZoneResult(qi=round(min(qi, 300), 4), zone="breach")

        # ── Low side ─────────────────────────────────────────
        if dr.side == "low":
            if value >= acc_lo:
                qi = _linear(value, acc_lo, ideal_lo, 50, 0)
                return ZoneResult(qi=round(qi, 4), zone="acceptable")
            # Below acceptable lower bound → deficient
            qi = 50 + _linear(value, 0, acc_lo, 50, 0) if acc_lo > 0 else 100
            return ZoneResult(qi=round(min(qi, 300), 4), zone="deficient")

        return ZoneResult(qi=0.0, zone="ideal")
