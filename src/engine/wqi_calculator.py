"""
wqi_calculator.py

Public API for the WQI engine.
Everything outside this module should only touch these functions.

Functions:
    calculate_wqi           → single sample dict
    calculate_wqi_batch     → list of sample dicts
    calculate_wqi_from_csv  → CSV file path
"""

import pandas as pd
from pathlib import Path
from .weighting_engine import WeightingEngine, load_profile


# ── Single sample ─────────────────────────────────────────────────────────────

def calculate_wqi(sample: dict, profile_id: str = "bis_drinking") -> dict:
    """
    Compute WQI for a single water sample.

    Args:
        sample:     { "pH": 7.2, "TDS": 310, ... }
        profile_id: profile to use (default: "bis_drinking")

    Returns:
        {
            status, wqi, classification, confidence,
            flags, dominant_issues, sub_indices
        }
    """
    engine = WeightingEngine(profile_id)
    return engine.compute(sample)


# ── Batch ─────────────────────────────────────────────────────────────────────

def calculate_wqi_batch(samples: list, profile_id: str = "bis_drinking") -> list:
    """
    Compute WQI for a list of sample dicts.
    Reuses one engine instance across all samples.

    Args:
        samples:    [ { "pH": 7.2, ... }, { "pH": 6.8, ... }, ... ]
        profile_id: profile to use

    Returns:
        List of result dicts, same order as input.
    """
    engine  = WeightingEngine(profile_id)
    results = []

    for i, sample in enumerate(samples):
        try:
            result = engine.compute(sample)
        except Exception as e:
            result = {
                "status":         "ERROR",
                "wqi":            None,
                "classification": "ERROR",
                "confidence":     0.0,
                "flags":          [{"param": "engine", "code": "COMPUTE_ERROR",
                                    "severity": "critical", "message": str(e), "qi": None}],
                "dominant_issues": [],
                "sub_indices":    {}
            }
        result["_index"] = i
        results.append(result)

    return results


# ── CSV ───────────────────────────────────────────────────────────────────────

def calculate_wqi_from_csv(
    csv_path: str,
    profile_id: str = "bis_drinking",
    meta_cols:  list = None,
) -> list:
    """
    Load samples from a CSV and compute WQI for each row.

    Parameter columns are auto-detected by matching against the profile.
    All other columns are treated as metadata and passed through in results.

    Args:
        csv_path:   Path to CSV file.
        profile_id: Profile to use.
        meta_cols:  Explicit list of metadata column names (optional).
                    If None, any column not in the profile is treated as metadata.

    Returns:
        List of result dicts, each including metadata columns.
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df     = pd.read_csv(path)
    engine = WeightingEngine(profile_id)
    params = set(engine.profile["parameters"].keys())

    # Detect which columns are params vs metadata
    param_cols = [c for c in df.columns if c in params]
    meta_cols  = meta_cols or [c for c in df.columns if c not in params]

    if not param_cols:
        raise ValueError(
            f"No matching parameter columns found in CSV.\n"
            f"CSV columns:     {list(df.columns)}\n"
            f"Profile expects: {sorted(params)}"
        )

    results = []
    for _, row in df.iterrows():
        # Build sample — use None for missing values (validator handles them)
        sample = {
            col: row[col] if pd.notna(row[col]) else None
            for col in param_cols
        }

        result = engine.compute(sample)

        # Attach metadata
        for mc in meta_cols:
            result[mc] = row[mc]

        results.append(result)

    return results


# ── Summary helper ────────────────────────────────────────────────────────────

def summarize_batch(results: list) -> dict:
    """
    Quick summary stats across a batch of results.

    Returns:
        {
            total, safe, non_compliant, unsafe, error,
            avg_wqi, avg_confidence,
            most_common_issues
        }
    """
    from collections import Counter

    total         = len(results)
    safe          = sum(1 for r in results if r["status"] == "SAFE")
    non_compliant = sum(1 for r in results if r["status"] == "NON_COMPLIANT")
    unsafe        = sum(1 for r in results if r["status"] == "UNSAFE")
    error         = sum(1 for r in results if r["status"] == "ERROR")

    wqi_values    = [r["wqi"] for r in results if r["wqi"] is not None]
    avg_wqi       = round(sum(wqi_values) / len(wqi_values), 2) if wqi_values else None

    conf_values   = [r["confidence"] for r in results]
    avg_confidence = round(sum(conf_values) / len(conf_values), 2) if conf_values else 0.0

    all_issues    = [p for r in results for p in r.get("dominant_issues", [])]
    most_common   = [issue for issue, _ in Counter(all_issues).most_common(5)]

    return {
        "total":              total,
        "safe":               safe,
        "non_compliant":      non_compliant,
        "unsafe":             unsafe,
        "error":              error,
        "avg_wqi":            avg_wqi,
        "avg_confidence":     avg_confidence,
        "most_common_issues": most_common,
    }