"""
flag_engine.py

Converts scoring results into semantic flags.
Flags are sorted by severity before output.

Severity hierarchy (high → low):
  critical  → HARD_GATE_BREACH         (UNSAFE — do not drink)
  violation → NON_RELAXABLE_VIOLATED   (compliance fail)
  warning   → PERMISSIBLE_EXCEEDED     (beyond acceptable, within permissible)
              BREACH                   (beyond all limits)
              HEALTH_PARAM_HIGH        (health-impact param in bad zone)
  info      → NEAR_LIMIT               (within 10% of acceptable boundary)
              AESTHETIC_ISSUE          (aesthetic/operational param elevated)
              NO_DATA                  (param missing, confidence penalized)
              SUSPECT                  (value looks like unit error)
"""

from dataclasses import dataclass, field
from typing import List, Optional


SEVERITY_ORDER = {"critical": 0, "violation": 1, "warning": 2, "info": 3}


@dataclass(order=True)
class Flag:
    severity_rank: int = field(init=False, repr=False)
    param:         str
    code:          str
    severity:      str       # "critical" | "violation" | "warning" | "info"
    message:       str
    qi:            Optional[float] = None

    def __post_init__(self):
        self.severity_rank = SEVERITY_ORDER.get(self.severity, 99)


class FlagEngine:

    def generate(self, param: str, spec: dict, zone: str, qi: float,
                 safe: bool, compliant: bool,
                 validation_flag: Optional[str] = None) -> List[Flag]:
        """
        Generate all flags for a single parameter result.
        Returns a list (usually 0–2 flags).
        """
        flags   = []
        layer   = spec["layer"]
        impact  = spec.get("impact", "health")

        # ── Validation flags ─────────────────────────────────────────────────
        if validation_flag == "NO_DATA":
            flags.append(Flag(param=param, code="NO_DATA", severity="info",
                              message=f"{param}: data missing — excluded from scoring"))
            return flags

        if validation_flag == "SUSPECT":
            flags.append(Flag(param=param, code="SUSPECT", severity="info",
                              message=f"{param}: value suspect, likely unit error"))
            return flags

        if validation_flag == "INVALID":
            flags.append(Flag(param=param, code="INVALID", severity="warning",
                              message=f"{param}: invalid value — excluded from scoring"))
            return flags

        # ── Hard gate breach ─────────────────────────────────────────────────
        if layer == "hard_gate" and not safe:
            flags.append(Flag(param=param, code="HARD_GATE_BREACH", severity="critical",
                              message=f"{param}: exceeds hard safety limit — water is UNSAFE",
                              qi=qi))
            return flags

        # ── Non-relaxable violation ──────────────────────────────────────────
        if layer == "non_relaxable" and not compliant:
            flags.append(Flag(param=param, code="NON_RELAXABLE_VIOLATED", severity="violation",
                              message=f"{param}: outside acceptable range — compliance FAIL",
                              qi=qi))

        # ── Zone-based warnings ──────────────────────────────────────────────
        if zone == "breach":
            flags.append(Flag(param=param, code="BREACH", severity="warning",
                              message=f"{param}: exceeds all permissible limits",
                              qi=qi))

        elif zone == "permissible":
            flags.append(Flag(param=param, code="PERMISSIBLE_EXCEEDED",
                              severity="warning",
                              message=f"{param}: beyond acceptable, within permissible limit",
                              qi=qi))

        elif zone in ("acceptable", "deficient") and impact == "health" and qi > 40:
            flags.append(Flag(param=param, code="HEALTH_PARAM_HIGH", severity="warning",
                              message=f"{param}: health-impacting param approaching limit",
                              qi=qi))

        elif zone in ("acceptable", "deficient") and impact == "aesthetic" and qi > 40:
            flags.append(Flag(param=param, code="AESTHETIC_ISSUE", severity="info",
                              message=f"{param}: aesthetic param elevated",
                              qi=qi))

        # ── Near-limit info ──────────────────────────────────────────────────
        elif zone == "acceptable" and qi > 45:
            flags.append(Flag(param=param, code="NEAR_LIMIT", severity="info",
                              message=f"{param}: approaching acceptable limit",
                              qi=qi))

        return flags

    def sort(self, flags: List[Flag]) -> List[Flag]:
        return sorted(flags)
