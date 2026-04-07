"""
Regression tests for profile-source corrections.
"""

from server import _load_profile


def test_who_drinking_includes_mercury_hard_gate():
    profile = _load_profile("who")
    mercury = profile["parameters"]["Mercury"]

    assert mercury["layer"] == "hard_gate"
    assert mercury["limits"]["acceptable"] == 0.006


def test_bis_drinking_iron_no_longer_has_relaxation():
    profile = _load_profile("drinking")
    iron = profile["parameters"]["iron"]

    assert iron["relaxable"] is False
    assert iron["limits"]["acceptable"] == 0.3
    assert iron["limits"]["permissible"] == 0.3


def test_bis_drinking_includes_added_health_parameters():
    profile = _load_profile("drinking")

    assert profile["parameters"]["ammonia"]["limits"]["acceptable"] == 0.5
    assert profile["parameters"]["selenium"]["limits"]["acceptable"] == 0.01
    assert profile["parameters"]["nitrite"]["limits"]["acceptable"] == 1.0
    assert profile["parameters"]["manganese"]["limits"]["permissible"] == 0.3


def test_fao_agriculture_corrected_manganese_and_zinc_limits():
    profile = _load_profile("agriculture")

    assert profile["parameters"]["Manganese"]["limits"]["permissible"] == 0.2
    assert profile["parameters"]["Zinc"]["limits"]["permissible"] == 2.0


def test_aquaculture_tightens_mercury_and_lead_notes_backed_limits():
    profile = _load_profile("aquaculture")

    assert profile["parameters"]["Mercury"]["limits"]["acceptable"] == 0.00077
    assert profile["parameters"]["Lead"]["limits"]["acceptable"] == 0.065
