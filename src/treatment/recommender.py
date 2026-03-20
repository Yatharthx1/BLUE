"""
recommender.py
Rule-based water treatment recommendation engine.
Phase 4 will layer ML predictions on top of these rules.
"""

from loguru import logger


TREATMENT_RULES = {
    "pH": {
        "low":  (0, 6.5, "Add lime (Ca(OH)2) or soda ash to raise pH. Aeration may help."),
        "high": (8.5, 14, "Add CO2 or dilute acid (HCl). Check for carbonate hardness."),
    },
    "TDS": {
        "high": (500, float("inf"), "Reverse Osmosis (RO) recommended. Check ion exchange units."),
    },
    "turbidity": {
        "high": (1, float("inf"), "Coagulation-flocculation + filtration. Check sedimentation tanks."),
    },
    "nitrates": {
        "high": (45, float("inf"), "Ion exchange or biological denitrification required."),
    },
    "fluoride": {
        "high": (1.5, float("inf"), "Activated alumina or RO treatment recommended."),
        "low":  (0, 0.5, "Consider fluoridation per local health guidelines."),
    },
    "dissolved_oxygen": {
        "low": (0, 4, "Aeration required. Check for organic pollution upstream."),
    },
    "BOD": {
        "high": (3, float("inf"), "Biological treatment (activated sludge) needed. High organic load detected."),
    },
    "coliform": {
        "high": (0, float("inf"), "Immediate disinfection required: chlorination, UV, or ozonation."),
    },
    "arsenic": {
        "high": (0.01, float("inf"), "Oxidation + coagulation-filtration or RO. Health risk — do not consume."),
    },
    "lead": {
        "high": (0.01, float("inf"), "Check pipe corrosion. Coagulation or RO. Health risk — do not consume."),
    },
}


def get_recommendations(sample: dict, standard_name: str = "bis") -> list[dict]:
    """
    Generate treatment recommendations based on measured parameter values.

    Args:
        sample: { parameter: value }
        standard_name: used for future ML-aware context

    Returns:
        List of recommendation dicts
    """
    recommendations = []

    for param, value in sample.items():
        rules = TREATMENT_RULES.get(param)
        if not rules:
            continue
        for severity, (lo, hi, advice) in rules.items():
            if lo <= value <= hi if hi != float("inf") else value > lo:
                recommendations.append({
                    "parameter": param,
                    "measured_value": value,
                    "issue": severity,
                    "recommendation": advice,
                    "priority": "HIGH" if param in ("coliform", "arsenic", "lead") else "MEDIUM",
                })
                logger.info(f"[{param}] {severity.upper()} — {advice}")

    if not recommendations:
        recommendations.append({
            "parameter": "ALL",
            "issue": "none",
            "recommendation": "Water parameters within acceptable limits. Routine monitoring advised.",
            "priority": "LOW",
        })

    return recommendations
