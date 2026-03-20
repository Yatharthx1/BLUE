import sys
sys.path.insert(0, 'src')

from engine.wqi_calculator import calculate_wqi

SAMPLE = {
    "pH": 7.2,
    "TDS": 310,
    "turbidity": 0.8,
    "nitrates": 32,
    "fluoride": 0.9,
    "dissolved_oxygen": 6.5,
    "BOD": 1.8,
    "coliform": 0,
}

def test_wqi_returns_dict():
    result = calculate_wqi(SAMPLE, standard_name="bis")
    assert isinstance(result, dict)
    assert "wqi" in result
    assert "classification" in result

def test_wqi_range():
    result = calculate_wqi(SAMPLE, standard_name="bis")
    assert 0 <= result["wqi"] <= 300

def test_classification_type():
    result = calculate_wqi(SAMPLE, standard_name="bis")
    assert isinstance(result["classification"], str)

if __name__ == "__main__":
    result = calculate_wqi(SAMPLE, "bis")
    print(f"WQI: {result['wqi']} — {result['classification']}")
