"""
Regression tests for frontend-facing profile parameter definitions.
"""

import pytest

from server import _build_confidence_details, _build_frontend_param_defs, _load_profile


@pytest.mark.parametrize("profile_key", ["agriculture", "industrial", "aquaculture"])
def test_frontend_param_defs_cover_all_profile_parameters(profile_key):
    profile_cfg = _load_profile(profile_key)

    param_defs = _build_frontend_param_defs(profile_cfg["profile_id"], profile_cfg)

    assert [param["id"] for param in param_defs] == list(profile_cfg["parameters"].keys())


@pytest.mark.parametrize("profile_key", ["agriculture", "industrial", "aquaculture"])
def test_confidence_details_expected_count_matches_profile_parameters(profile_key):
    profile_cfg = _load_profile(profile_key)

    details = _build_confidence_details(
        {"confidence": 0.0, "sub_indices": {}},
        profile_cfg["profile_id"],
        profile_cfg,
    )

    assert details["expected_count"] == len(profile_cfg["parameters"])
    assert details["provided_count"] == 0
    assert len(details["missing_params"]) == len(profile_cfg["parameters"])
