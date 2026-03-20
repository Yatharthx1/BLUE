"""
wqi_calculator.py
High-level entry point. Ties standards + weighting engine together.
"""

from .standards import load_standard
from .weighting_engine import WeightingEngine


def calculate_wqi(sample: dict, standard_name: str = "bis", custom_weights: dict = None) -> dict:
    """
    Main function to compute WQI.

    Args:
        sample: dict of { parameter_name: measured_value }
        standard_name: 'bis' | 'who' (or any future standard)
        custom_weights: optional override weights

    Returns:
        Full WQI result dict
    """
    standard = load_standard(standard_name)
    engine = WeightingEngine(standard, custom_weights)
    return engine.compute_wqi(sample)
