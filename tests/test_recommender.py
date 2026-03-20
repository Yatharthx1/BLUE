import sys
sys.path.insert(0, 'src')

from treatment.recommender import get_recommendations

def test_contaminated_sample():
    sample = {"pH": 5.5, "coliform": 8, "nitrates": 60}
    recs = get_recommendations(sample)
    params = [r["parameter"] for r in recs]
    assert "coliform" in params
    assert "nitrates" in params

def test_clean_sample():
    sample = {"pH": 7.2, "TDS": 200, "dissolved_oxygen": 7.0}
    recs = get_recommendations(sample)
    assert recs[0]["priority"] == "LOW"

if __name__ == "__main__":
    recs = get_recommendations({"pH": 5.5, "coliform": 8})
    for r in recs:
        print(f"[{r['priority']}] {r['parameter']}: {r['recommendation']}")
