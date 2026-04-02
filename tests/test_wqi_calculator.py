"""
tests/test_wqi_calculator.py
Phase 1 test suite — weighting engine + calculator.
"""
import sys
sys.path.insert(0, 'src')

import pytest
from src.engine.wqi_calculator import (
    calculate_wqi,
    calculate_wqi_batch,
    calculate_wqi_from_csv,
    summarize_batch,
)
from src.engine.weighting_engine import WeightingEngine


# ── Fixtures ──────────────────────────────────────────────────────────────────

CLEAN = {
    "pH": 7.2, "TDS": 310, "turbidity": 0.8,
    "fluoride": 0.9, "dissolved_oxygen": 6.5,
    "BOD": 1.8, "coliform": 0,
}

CONTAMINATED = {                        # coliform + nitrates breach hard gate
    "pH": 6.1, "TDS": 620, "turbidity": 3.2,
    "nitrates": 51, "fluoride": 2.1,
    "dissolved_oxygen": 3.8, "BOD": 5.2, "coliform": 4,
}

PH_VIOLATION = {                        # pH outside acceptable, nothing else wrong
    "pH": 6.0, "TDS": 200, "turbidity": 0.5,
    "fluoride": 0.8, "dissolved_oxygen": 8.0,
    "BOD": 1.0, "coliform": 0,
}

PERFECT = {                             # all params at or near ideal
    "pH": 7.5, "TDS": 200, "turbidity": 0.0,
    "nitrates": 0, "fluoride": 0.8,
    "dissolved_oxygen": 14.6, "BOD": 0,
    "coliform": 0, "hardness": 0,
    "chlorides": 0, "sulphate": 0,
}

MISSING_DATA = {                        # several params absent
    "pH": 7.0, "TDS": 300,
}


# ── Output structure ──────────────────────────────────────────────────────────

class TestOutputStructure:

    def test_required_keys_present(self):
        r = calculate_wqi(CLEAN)
        for key in ("status", "wqi", "classification", "confidence",
                    "flags", "dominant_issues", "sub_indices"):
            assert key in r, f"Missing key: {key}"

    def test_flags_are_list_of_dicts(self):
        r = calculate_wqi(CLEAN)
        assert isinstance(r["flags"], list)
        for f in r["flags"]:
            assert "param" in f and "code" in f and "severity" in f

    def test_sub_indices_has_scored_params(self):
        r = calculate_wqi(CLEAN)
        assert len(r["sub_indices"]) > 0

    def test_confidence_between_0_and_1(self):
        r = calculate_wqi(CLEAN)
        assert 0.0 <= r["confidence"] <= 1.0


# ── Layer 1: Hard Gate ────────────────────────────────────────────────────────

class TestHardGate:

    def test_coliform_breach_gives_unsafe(self):
        r = calculate_wqi({"coliform": 1, "pH": 7.0, "TDS": 200})
        assert r["status"] == "UNSAFE"

    def test_coliform_breach_gives_no_wqi(self):
        r = calculate_wqi({"coliform": 1, "pH": 7.0, "TDS": 200})
        assert r["wqi"] is None

    def test_nitrates_breach_gives_unsafe(self):
        r = calculate_wqi({"nitrates": 46, "pH": 7.0, "TDS": 200, "coliform": 0})
        assert r["status"] == "UNSAFE"

    def test_arsenic_breach_gives_unsafe(self):
        r = calculate_wqi({"arsenic": 0.02, "pH": 7.0, "TDS": 200, "coliform": 0})
        assert r["status"] == "UNSAFE"

    def test_lead_breach_gives_unsafe(self):
        r = calculate_wqi({"lead": 0.02, "pH": 7.0, "TDS": 200, "coliform": 0})
        assert r["status"] == "UNSAFE"

    def test_hard_gate_flag_is_critical(self):
        r = calculate_wqi({"coliform": 5, "pH": 7.0})
        critical = [f for f in r["flags"] if f["severity"] == "critical"]
        assert len(critical) > 0

    def test_hard_gate_flag_sorted_first(self):
        r = calculate_wqi(CONTAMINATED)
        assert r["flags"][0]["severity"] == "critical"

    def test_coliform_zero_is_safe(self):
        r = calculate_wqi({"coliform": 0, "pH": 7.0, "TDS": 200})
        assert r["status"] != "UNSAFE"

    def test_nitrates_at_limit_is_safe(self):
        r = calculate_wqi({"nitrates": 45, "pH": 7.0, "TDS": 200, "coliform": 0})
        assert r["status"] != "UNSAFE"


# ── Layer 2a: Non-Relaxable ───────────────────────────────────────────────────

class TestNonRelaxable:

    def test_ph_breach_gives_non_compliant(self):
        r = calculate_wqi(PH_VIOLATION)
        assert r["status"] == "NON_COMPLIANT"

    def test_ph_breach_still_computes_wqi(self):
        r = calculate_wqi(PH_VIOLATION)
        assert r["wqi"] is not None

    def test_ph_breach_flag_is_violation(self):
        r = calculate_wqi(PH_VIOLATION)
        violations = [f for f in r["flags"] if f["severity"] == "violation"]
        assert any(f["param"] == "pH" for f in violations)

    def test_ph_in_range_no_violation(self):
        r = calculate_wqi(CLEAN)
        violations = [f for f in r["flags"] if f["code"] == "NON_RELAXABLE_VIOLATED"]
        assert len(violations) == 0


# ── Layer 2b: Relaxable Scoring ───────────────────────────────────────────────

class TestRelaxableScoring:

    def test_perfect_sample_low_wqi(self):
        r = calculate_wqi(PERFECT)
        assert r["wqi"] is not None
        assert r["wqi"] < 10.0

    def test_wqi_is_float(self):
        r = calculate_wqi(CLEAN)
        assert isinstance(r["wqi"], float)

    def test_wqi_non_negative(self):
        r = calculate_wqi(CLEAN)
        assert r["wqi"] >= 0

    def test_contaminated_has_no_wqi(self):
        r = calculate_wqi(CONTAMINATED)
        assert r["wqi"] is None


# ── Direction handling ────────────────────────────────────────────────────────

class TestDirectionHandling:

    def test_dissolved_oxygen_at_ideal_is_zero_qi(self):
        engine = WeightingEngine("bis_drinking")
        from src.engine.direction_handler import DirectionHandler
        from src.engine.zone_mapper import ZoneMapper
        spec   = engine.params["dissolved_oxygen"]
        dh     = DirectionHandler()
        zm     = ZoneMapper()
        dr     = dh.compute(14.6, "down_bad", spec["limits"])
        zr     = zm.map(14.6, dr, "down_bad", spec["limits"], True)
        assert zr.qi == 0.0

    def test_dissolved_oxygen_at_floor_is_100_qi(self):
        engine = WeightingEngine("bis_drinking")
        from src.engine.direction_handler import DirectionHandler
        from src.engine.zone_mapper import ZoneMapper
        spec   = engine.params["dissolved_oxygen"]
        dh     = DirectionHandler()
        zm     = ZoneMapper()
        dr     = dh.compute(4.0, "down_bad", spec["limits"])
        zr     = zm.map(4.0, dr, "down_bad", spec["limits"], True)
        assert zr.qi == 100.0

    def test_tds_both_bad_high_side(self):
        engine = WeightingEngine("bis_drinking")
        from src.engine.direction_handler import DirectionHandler
        spec = engine.params["TDS"]
        dh   = DirectionHandler()
        dr   = dh.compute(1000, "both_bad", spec["limits"])
        assert dr.side == "high"

    def test_tds_both_bad_in_range(self):
        engine = WeightingEngine("bis_drinking")
        from src.engine.direction_handler import DirectionHandler
        spec = engine.params["TDS"]
        dh   = DirectionHandler()
        dr   = dh.compute(200, "both_bad", spec["limits"])
        assert dr.side == "in_range"


# ── Classification ────────────────────────────────────────────────────────────

class TestClassification:

    def test_classify_excellent(self):
        assert WeightingEngine._classify(0)  == "Excellent"
        assert WeightingEngine._classify(25) == "Excellent"

    def test_classify_good(self):
        assert WeightingEngine._classify(26) == "Good"
        assert WeightingEngine._classify(50) == "Good"

    def test_classify_poor(self):
        assert WeightingEngine._classify(51) == "Poor"
        assert WeightingEngine._classify(75) == "Poor"

    def test_classify_very_poor(self):
        assert WeightingEngine._classify(76)  == "Very Poor"
        assert WeightingEngine._classify(100) == "Very Poor"

    def test_classify_unsuitable(self):
        assert WeightingEngine._classify(101) == "Unsuitable"

    def test_classify_none_is_unsafe(self):
        assert WeightingEngine._classify(None) == "UNSAFE"


# ── Confidence ────────────────────────────────────────────────────────────────

class TestConfidence:

    def test_full_sample_higher_confidence(self):
        r_full    = calculate_wqi(PERFECT)
        r_partial = calculate_wqi(MISSING_DATA)
        assert r_full["confidence"] > r_partial["confidence"]

    def test_missing_data_reduces_confidence(self):
        r = calculate_wqi(MISSING_DATA)
        assert r["confidence"] < 1.0

    def test_no_data_flag_generated(self):
        r     = calculate_wqi(MISSING_DATA)
        codes = [f["code"] for f in r["flags"]]
        assert "NO_DATA" in codes


# ── Validator ─────────────────────────────────────────────────────────────────

class TestValidator:

    def test_none_value_flagged(self):
        from src.engine.validator import ParameterValidator
        v  = ParameterValidator()
        vr = v.validate("TDS", None, {"limits": {"acceptable": 500}})
        assert not vr.valid
        assert vr.flag_code == "NO_DATA"

    def test_non_numeric_flagged(self):
        from src.engine.validator import ParameterValidator
        v  = ParameterValidator()
        vr = v.validate("TDS", "abc", {"limits": {"acceptable": 500}})
        assert not vr.valid
        assert vr.flag_code == "INVALID"

    def test_negative_flagged(self):
        from src.engine.validator import ParameterValidator
        v  = ParameterValidator()
        vr = v.validate("TDS", -5, {"limits": {"acceptable": 500}})
        assert not vr.valid
        assert vr.flag_code == "INVALID"

    def test_suspect_outlier_flagged(self):
        from src.engine.validator import ParameterValidator
        v  = ParameterValidator()
        vr = v.validate("TDS", 99999, {"limits": {"acceptable": 500}})
        assert not vr.valid
        assert vr.flag_code == "SUSPECT"

    def test_valid_value_passes(self):
        from src.engine.validator import ParameterValidator
        v  = ParameterValidator()
        vr = v.validate("TDS", 310, {"limits": {"acceptable": 500}})
        assert vr.valid


# ── Batch ─────────────────────────────────────────────────────────────────────

class TestBatch:

    def test_batch_returns_correct_count(self):
        results = calculate_wqi_batch([CLEAN, CONTAMINATED, PH_VIOLATION])
        assert len(results) == 3

    def test_batch_order_preserved(self):
        results = calculate_wqi_batch([CLEAN, CONTAMINATED])
        assert results[0]["_index"] == 0
        assert results[1]["_index"] == 1

    def test_batch_mixed_statuses(self):
        results  = calculate_wqi_batch([CLEAN, CONTAMINATED, PH_VIOLATION])
        statuses = {r["status"] for r in results}
        assert "SAFE"          in statuses
        assert "UNSAFE"        in statuses
        assert "NON_COMPLIANT" in statuses


# ── CSV loader ────────────────────────────────────────────────────────────────

class TestCSV:

    def test_csv_returns_correct_count(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        assert len(results) == 4

    def test_csv_metadata_passed_through(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        assert all("sample_id" in r for r in results)
        assert all("location"  in r for r in results)

    def test_csv_unsafe_samples_correct(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        by_id   = {r["sample_id"]: r for r in results}
        assert by_id["S002"]["status"] == "UNSAFE"
        assert by_id["S004"]["status"] == "UNSAFE"

    def test_csv_safe_samples_correct(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        by_id   = {r["sample_id"]: r for r in results}
        assert by_id["S001"]["status"] == "SAFE"
        assert by_id["S003"]["status"] == "SAFE"

    def test_csv_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            calculate_wqi_from_csv("data/samples/nonexistent.csv")


# ── Summary ───────────────────────────────────────────────────────────────────

class TestSummary:

    def test_summary_totals_correct(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        s       = summarize_batch(results)
        assert s["total"]  == 4
        assert s["safe"]   == 2
        assert s["unsafe"] == 2

    def test_summary_avg_wqi_excludes_unsafe(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        s       = summarize_batch(results)
        assert s["avg_wqi"] is not None
        assert s["avg_wqi"] > 0

    def test_summary_most_common_issues_is_list(self):
        results = calculate_wqi_from_csv("data/samples/sample_input.csv")
        s       = summarize_batch(results)
        assert isinstance(s["most_common_issues"], list)


if __name__ == "__main__":
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])