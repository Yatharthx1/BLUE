"""
weighting_engine.py
Computes sub-index scores and applies weights per parameter.
Formula: WQI = sum(Wi * qi) / sum(Wi)
where qi = ((Vi - Vi_ideal) / (Si - Vi_ideal)) * 100
"""

from .standards import WaterStandard
from loguru import logger


class WeightingEngine:
    def __init__(self, standard: WaterStandard, custom_weights: dict = None):
        self.standard = standard
        self.custom_weights = custom_weights or {}

    def _get_weight(self, param: str) -> float:
        return self.custom_weights.get(param, self.standard.parameters[param].weight)

    def compute_sub_index(self, param: str, value: float) -> float:
        """Compute qi for a single parameter."""
        spec = self.standard.parameters.get(param)
        if spec is None:
            logger.warning(f"Parameter '{param}' not in standard. Skipping.")
            return 0.0

        ideal = spec.ideal
        limit = spec.permissible[1]  # Use upper permissible limit as Si

        if limit == ideal:
            logger.warning(f"Limit equals ideal for '{param}'. Returning 0.")
            return 0.0

        qi = abs((value - ideal) / (limit - ideal)) * 100
        logger.debug(f"{param}: value={value}, qi={qi:.2f}")
        return round(qi, 4)

    def compute_wqi(self, sample: dict) -> dict:
        """
        Compute overall WQI for a water sample.
        sample: { 'pH': 7.2, 'TDS': 310, ... }
        Returns: { 'wqi': float, 'sub_indices': dict, 'classification': str }
        """
        total_weight = 0.0
        weighted_sum = 0.0
        sub_indices = {}

        for param, value in sample.items():
            if param not in self.standard.parameters:
                continue
            qi = self.compute_sub_index(param, value)
            wi = self._get_weight(param)
            sub_indices[param] = {"value": value, "qi": qi, "weight": wi}
            weighted_sum += wi * qi
            total_weight += wi

        wqi = weighted_sum / total_weight if total_weight > 0 else 0.0
        return {
            "wqi": round(wqi, 2),
            "sub_indices": sub_indices,
            "classification": self.classify(wqi),
            "standard_used": self.standard.standard,
        }

    @staticmethod
    def classify(wqi: float) -> str:
        if wqi <= 25:    return "Excellent"
        elif wqi <= 50:  return "Good"
        elif wqi <= 75:  return "Poor"
        elif wqi <= 100: return "Very Poor"
        else:            return "Unsuitable for Drinking"
