"""
main.py — Project UPD  |  Water Quality Index System
======================================================
Interactive terminal interface for the full WQI pipeline.

Usage:
    python main.py                        # interactive menu
    python main.py --sample               # enter a single sample manually
    python main.py --csv  path/to/f.csv   # analyse a CSV file
    python main.py --profile bis_drinking # set default profile

Workflow for each run:
    1. User picks a profile  (BIS / WHO / FAO / Aquaculture / Industrial)
    2. User picks input mode (manual entry | CSV | quick demo)
    3. WQI engine scores every parameter
    4. Treatment recommender generates prioritised advice
    5. Results are printed to the terminal
    6. Optional: export a PDF report
"""

import argparse
import csv
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path


# ── Dependency bootstrap ───────────────────────────────────────────────────────
# loguru is an optional dep; stub it so the engine loads even without install

try:
    import loguru  # noqa: F401
except ModuleNotFoundError:
    import types
    _lg = types.ModuleType("loguru")
    class _Logger:
        def info(self, *a, **k):    pass
        def warning(self, *a, **k): pass
        def debug(self, *a, **k):   pass
        def error(self, *a, **k):   pass
    _lg.logger = _Logger()
    sys.modules["loguru"] = _lg


# ── Colour helpers (ANSI, disabled on Windows if unsupported) ──────────────────

_USE_COLOR = sys.platform != "win32" or os.environ.get("TERM", "") != ""

def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text

def bold(t):    return _c("1", t)
def dim(t):     return _c("2", t)
def green(t):   return _c("32", t)
def yellow(t):  return _c("33", t)
def red(t):     return _c("31", t)
def cyan(t):    return _c("36", t)
def blue(t):    return _c("34", t)
def magenta(t): return _c("35", t)
def white(t):   return _c("97", t)

def _status_fmt(status: str) -> str:
    return {
        "SAFE":          green(bold("SAFE")),
        "NON_COMPLIANT": yellow(bold("NON_COMPLIANT")),
        "UNSAFE":        red(bold("UNSAFE")),
        "UNKNOWN":       dim("UNKNOWN"),
    }.get(status, status)

def _zone_fmt(zone: str) -> str:
    return {
        "ideal":       green("ideal"),
        "acceptable":  green("acceptable"),
        "permissible": yellow("permissible"),
        "breach":      red("breach"),
        "deficient":   red("deficient"),
    }.get(zone or "", dim(zone or "--"))

def _priority_fmt(p: str) -> str:
    return {
        "CRITICAL": red(bold("CRITICAL")),
        "HIGH":     red("HIGH"),
        "MEDIUM":   yellow("MEDIUM"),
        "LOW":      green("LOW"),
    }.get(p, p)

def _sev_fmt(s: str) -> str:
    return {
        "critical":  red(bold("CRITICAL")),
        "violation": red("VIOLATION"),
        "warning":   yellow("WARNING"),
        "info":      blue("INFO"),
    }.get(s, s)


# ── Print helpers ──────────────────────────────────────────────────────────────

SEP  = dim("─" * 70)
SEP2 = dim("═" * 70)

def banner():
    print()
    print(cyan(bold("  ██╗    ██╗ ██████╗ ██╗")))
    print(cyan(bold("  ██║    ██║██╔═══██╗██║")))
    print(cyan(bold("  ██║ █╗ ██║██║   ██║██║")))
    print(cyan(bold("  ██║███╗██║██║▄▄ ██║██║")))
    print(cyan(bold("  ╚███╔███╔╝╚██████╔╝██║")))
    print(cyan(bold("   ╚══╝╚══╝  ╚══▀▀═╝ ╚═╝")))
    print()
    print(bold("  Project UPD — Water Quality Index System"))
    print(dim("  Phases: WQI Engine · Profiles · Treatment · Reports"))
    print()

def hr(title: str = ""):
    if title:
        pad = (68 - len(title)) // 2
        print(dim("─" * pad) + " " + bold(title) + " " + dim("─" * pad))
    else:
        print(SEP)

def section(title: str):
    print()
    print(SEP2)
    print(f"  {bold(title)}")
    print(SEP2)

def col(label: str, value: str, width: int = 24):
    print(f"  {dim(label.ljust(width))} {value}")


# ── Profile registry ───────────────────────────────────────────────────────────

PROFILES = {
    "1": ("bis_drinking",    "BIS IS:10500:2012  —  Drinking Water (India)"),
    "2": ("who_drinking",    "WHO 2022          —  Drinking Water (Global)"),
    "3": ("fao_agriculture", "FAO Ayers-Westcot  —  Agriculture / Irrigation"),
    "4": ("aquaculture",     "Custom            —  Aquaculture / Fish Farming"),
    "5": ("industrial",      "Custom            —  Industrial / Boiler Feed"),
}

PROFILE_PARAMS = {
    "bis_drinking":    {
        "coliform": ("Coliform bacteria", "MPN/100mL"),
        "arsenic":  ("Arsenic",           "mg/L"),
        "lead":     ("Lead",              "mg/L"),
        "nitrates": ("Nitrates",          "mg/L"),
        "pH":       ("pH",                "dimensionless"),
        "turbidity":("Turbidity",         "NTU"),
        "TDS":      ("TDS",               "mg/L"),
        "hardness": ("Hardness",          "mg/L"),
        "chlorides":("Chlorides",         "mg/L"),
        "sulphate": ("Sulphate",          "mg/L"),
        "fluoride": ("Fluoride",          "mg/L"),
        "iron":     ("Iron",              "mg/L"),
        "dissolved_oxygen": ("Dissolved Oxygen", "mg/L"),
        "BOD":      ("BOD",               "mg/L"),
    },
    "who_drinking": {
        "coliform":  ("Coliform bacteria","MPN/100mL"),
        "arsenic":   ("Arsenic",          "mg/L"),
        "lead":      ("Lead",             "mg/L"),
        "nitrates":  ("Nitrates",         "mg/L"),
        "nitrites":  ("Nitrites",         "mg/L"),
        "cadmium":   ("Cadmium",          "mg/L"),
        "pH":        ("pH",               "dimensionless"),
        "turbidity": ("Turbidity",        "NTU"),
        "TDS":       ("TDS",              "mg/L"),
        "hardness":  ("Hardness",         "mg/L"),
        "chlorides": ("Chlorides",        "mg/L"),
        "sulphate":  ("Sulphate",         "mg/L"),
        "fluoride":  ("Fluoride",         "mg/L"),
        "iron":      ("Iron",             "mg/L"),
        "manganese": ("Manganese",        "mg/L"),
        "dissolved_oxygen": ("DO",        "mg/L"),
        "BOD":       ("BOD",              "mg/L"),
    },
    "fao_agriculture": {
        "pH":         ("pH",              "dimensionless"),
        "EC":         ("EC",              "dS/m"),
        "SAR":        ("SAR",             "dimensionless"),
        "TDS":        ("TDS",             "mg/L"),
        "Boron":      ("Boron",           "mg/L"),
        "Chloride":   ("Chloride",        "mg/L"),
        "Sodium":     ("Sodium",          "mg/L"),
        "Nitrate_N":  ("Nitrate-N",       "mg/L"),
        "Bicarbonate":("Bicarbonate",     "mg/L"),
        "Sulfate":    ("Sulfate",         "mg/L"),
        "Iron":       ("Iron",            "mg/L"),
        "Manganese":  ("Manganese",       "mg/L"),
        "Zinc":       ("Zinc",            "mg/L"),
        "Copper":     ("Copper",          "mg/L"),
        "Fluoride":   ("Fluoride",        "mg/L"),
        "Arsenic":    ("Arsenic",         "mg/L"),
        "Cadmium":    ("Cadmium",         "mg/L"),
        "Lead":       ("Lead",            "mg/L"),
        "Mercury":    ("Mercury",         "mg/L"),
        "Selenium":   ("Selenium",        "mg/L"),
    },
    "aquaculture": {
        "pH":         ("pH",              "dimensionless"),
        "DO":         ("Dissolved Oxygen","mg/L"),
        "Ammonia_N":  ("Ammonia-N",       "mg/L"),
        "Nitrite":    ("Nitrite",         "mg/L"),
        "H2S":        ("Hydrogen Sulphide","mg/L"),
        "Chlorine":   ("Chlorine",        "mg/L"),
        "Copper":     ("Copper",          "mg/L"),
        "Zinc":       ("Zinc",            "mg/L"),
        "Mercury":    ("Mercury",         "mg/L"),
        "Arsenic":    ("Arsenic",         "mg/L"),
        "Lead":       ("Lead",            "mg/L"),
        "Temperature":("Temperature",     "degC"),
        "Nitrate":    ("Nitrate",         "mg/L"),
        "CO2":        ("Free CO2",        "mg/L"),
        "BOD":        ("BOD",             "mg/L"),
        "Turbidity":  ("Turbidity",       "NTU"),
        "Alkalinity": ("Alkalinity",      "mg/L"),
        "Hardness":   ("Hardness",        "mg/L"),
        "TDS":        ("TDS",             "mg/L"),
        "Iron":       ("Iron",            "mg/L"),
    },
    "industrial": {
        "pH":         ("pH",              "dimensionless"),
        "Alkalinity": ("Alkalinity",      "mg/L"),
        "Chloride":   ("Chloride",        "mg/L"),
        "TDS":        ("TDS",             "mg/L"),
        "Hardness":   ("Hardness",        "mg/L"),
        "Silica":     ("Silica",          "mg/L"),
        "Iron":       ("Iron",            "mg/L"),
        "DO":         ("Dissolved Oxygen","mg/L"),
        "Copper":     ("Copper",          "mg/L"),
        "Manganese":  ("Manganese",       "mg/L"),
        "Arsenic":    ("Arsenic",         "mg/L"),
        "Lead":       ("Lead",            "mg/L"),
        "Mercury":    ("Mercury",         "mg/L"),
        "Sulfate":    ("Sulfate",         "mg/L"),
        "Turbidity":  ("Turbidity",       "NTU"),
        "COD":        ("COD",             "mg/L"),
        "Oil_Grease": ("Oil & Grease",    "mg/L"),
        "Phosphate":  ("Phosphate",       "mg/L"),
        "Zinc":       ("Zinc",            "mg/L"),
    },
}

DEMO_SAMPLES = {
    "bis_drinking": {
        "sample": {"pH":7.2,"TDS":310,"hardness":180,"turbidity":0.8,
                   "nitrates":32,"fluoride":0.9,"chlorides":210,
                   "dissolved_oxygen":6.5,"BOD":1.8,"coliform":0},
        "meta": {"location": "Indore Zone A (Demo)", "sample_id": "DEMO-001"},
    },
    "who_drinking": {
        "sample": {"pH":6.1,"TDS":620,"hardness":260,"turbidity":3.2,
                   "nitrates":51,"fluoride":2.1,"chlorides":280,
                   "dissolved_oxygen":3.8,"BOD":5.2,"coliform":4},
        "meta": {"location": "Zone B (Demo)", "sample_id": "DEMO-002"},
    },
    "fao_agriculture": {
        "sample": {"pH":7.4,"EC":1.2,"SAR":5.1,"TDS":820,
                   "Boron":0.5,"Chloride":180,"Sodium":180,
                   "Nitrate_N":8,"Bicarbonate":300,"Sulfate":200},
        "meta": {"location": "Farm Site (Demo)", "sample_id": "DEMO-AGR"},
    },
    "aquaculture": {
        "sample": {"pH":7.8,"DO":6.5,"Ammonia_N":0.015,"Nitrite":0.05,
                   "Temperature":28,"Nitrate":12,"BOD":3.5,
                   "Turbidity":12,"Alkalinity":95,"Hardness":110,"TDS":380},
        "meta": {"location": "Fish Farm (Demo)", "sample_id": "DEMO-AQ"},
    },
    "industrial": {
        "sample": {"pH":8.6,"Alkalinity":180,"Chloride":85,"TDS":420,
                   "Hardness":38,"Silica":3.2,"Iron":0.05,"DO":0.08,
                   "Turbidity":4,"Sulfate":150},
        "meta": {"location": "Boiler Feed (Demo)", "sample_id": "DEMO-IND"},
    },
}


# ── Input helpers ──────────────────────────────────────────────────────────────

def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"  {prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        raise SystemExit(0)
    return val if val else default

def _ask_float(prompt: str, unit: str, required: bool = False) -> float | None:
    unit_str = f"  {dim(unit)}" if unit and unit != "dimensionless" else ""
    full_prompt = f"{prompt}{unit_str}"
    while True:
        raw = _ask(full_prompt, default="" if required else "skip")
        if raw.lower() in ("", "skip", "s", "-"):
            if required:
                print(red("  This parameter cannot be skipped."))
                continue
            return None
        try:
            return float(raw)
        except ValueError:
            print(red(f"  Invalid number: '{raw}'. Try again."))

def _choose(prompt: str, options: dict, default: str = "1") -> str:
    """Display a numbered menu and return the chosen key."""
    print()
    for key, label in options.items():
        marker = cyan(f"  [{key}]")
        print(f"{marker} {label}")
    print()
    while True:
        choice = _ask(prompt, default=default)
        if choice in options:
            return choice
        print(red(f"  Invalid choice '{choice}'. Enter one of: {', '.join(options)}."))


# ── Profile selection ──────────────────────────────────────────────────────────

def select_profile() -> tuple[str, str]:
    section("SELECT WATER USE PROFILE")
    opts = {k: v[1] for k, v in PROFILES.items()}
    key  = _choose("Select profile", opts)
    pid, plabel = PROFILES[key]
    print()
    print(f"  Profile: {cyan(bold(plabel))}")
    return pid, plabel


# ── Manual sample entry ────────────────────────────────────────────────────────

def enter_sample_manually(profile_id: str) -> tuple[dict, dict]:
    section("ENTER WATER SAMPLE PARAMETERS")
    params = PROFILE_PARAMS[profile_id]

    print(f"  Enter measured values for {cyan(bold(profile_id))}.")
    print(dim("  Press Enter to skip optional parameters (marked as skip)."))
    print(dim("  Hard-gate parameters (coliform, arsenic, lead, etc.) cannot be skipped."))
    print()

    # Hard gate params that must be entered if profile has them
    hard_gates = {"coliform", "arsenic", "lead", "nitrates", "nitrites",
                  "cadmium", "mercury", "selenium", "H2S", "Chlorine",
                  "Ammonia_N", "Silica", "Hardness"}

    sample = {}
    for key, (label, unit) in params.items():
        required = key in hard_gates
        tag      = red(" *required") if required else dim(" (skip=Enter)")
        val      = _ask_float(f"{label}{tag}", unit, required=required)
        if val is not None:
            sample[key] = val

    print()
    hr("SAMPLE METADATA")
    sample_id = _ask("Sample ID", default=f"S{datetime.now().strftime('%H%M%S')}")
    location  = _ask("Location / site name", default="Unknown")
    tested_by = _ask("Tested by", default="")
    lab_ref   = _ask("Lab reference", default="")

    meta = {
        "sample_id":  sample_id,
        "location":   location,
        "profile_id": profile_id,
        "tested_by":  tested_by,
        "lab_ref":    lab_ref,
        "date":       datetime.now().strftime("%d %b %Y"),
    }
    return sample, meta


# ── CSV loading ────────────────────────────────────────────────────────────────

def load_csv_path() -> str:
    section("LOAD CSV FILE")
    print(dim("  Expected columns: any parameter names + optional metadata columns."))
    print(dim("  Example: sample_id,location,pH,TDS,turbidity,..."))
    print()
    while True:
        path = _ask("CSV file path")
        if Path(path).is_file():
            return path
        print(red(f"  File not found: '{path}'. Try again."))


# ── Results display ────────────────────────────────────────────────────────────

def _wqi_bar(wqi: float, width: int = 30) -> str:
    """ASCII progress bar for WQI (0=green, 100=red limit)."""
    pct   = min(wqi / 100.0, 1.0)
    filled = int(pct * width)
    bar    = "█" * filled + "░" * (width - filled)
    if pct < 0.5:
        return green(bar)
    elif pct < 1.0:
        return yellow(bar)
    else:
        return red(bar)

def print_result(result: dict, meta: dict, profile_id: str):
    section("WQI ANALYSIS RESULT")
    status  = result.get("status", "UNKNOWN")
    wqi     = result.get("wqi")
    cls     = result.get("classification", "--")
    conf    = result.get("confidence", 0)

    col("Sample ID",     cyan(meta.get("sample_id", "--")))
    col("Location",      meta.get("location", "--"))
    col("Profile",       profile_id)
    col("Date",          meta.get("date", "--"))
    print()

    # Big status line
    print(f"  {bold('Overall Status')}  :  {_status_fmt(status)}")
    if wqi is not None:
        print(f"  {bold('WQI Score')}      :  {cyan(bold(f'{wqi:.2f}'))}  {_wqi_bar(wqi)}  {dim(cls)}")
    else:
        print(f"  {bold('WQI Score')}      :  {red('N/A (UNSAFE — hard gate breached)')}")
    print(f"  {bold('Classification')} :  {cyan(cls)}")
    print(f"  {bold('Confidence')}     :  {conf*100:.0f}%  {dim(f'({int(conf*100)}% of expected parameters provided)')}")

    dominant = result.get("dominant_issues", [])
    if dominant:
        print(f"  {bold('Dominant issues')} :  {red(', '.join(dominant))}")

    # Sub-indices table
    sub = result.get("sub_indices", {})
    if sub:
        print()
        hr("Parameter Scores")
        print(f"  {'Parameter':<22} {'Value':>10}  {'Zone':<14} {'qi':>6}  {'Layer':<16} {'Impact'}")
        print(dim("  " + "-" * 80))
        for param, info in sorted(sub.items()):
            qi    = info.get("qi")
            zone  = info.get("zone") or "--"
            value = info.get("value")
            layer = info.get("layer") or "--"
            imp   = info.get("impact") or "--"

            qi_str  = f"{qi:6.1f}" if qi is not None else "   N/A"
            val_str = f"{value:>10.3g}" if isinstance(value, (int, float)) else f"{'--':>10}"
            print(f"  {cyan(param):<31} {val_str}  {_zone_fmt(zone):<23} {qi_str}  "
                  f"{dim(layer):<16} {dim(imp)}")

    # Flags
    flags = result.get("flags", [])
    if flags:
        print()
        hr("Diagnostic Flags")
        for f in flags:
            sev = f.get("severity", "info")
            print(f"  {_sev_fmt(sev):<22} {dim(f.get('code','')):<28} {f.get('message','')}")


def print_recommendations(recs: dict):
    section("TREATMENT RECOMMENDATIONS")
    rec_list = recs.get("recommendations", [])
    summary  = recs.get("summary", {})

    if summary:
        c = summary.get("critical", 0)
        h = summary.get("high", 0)
        m = summary.get("medium", 0)
        l = summary.get("low", 0)
        action = summary.get("action_required", False)
        print(f"  Action required: {'  ' + red(bold('YES — treat before use')) if action else green('No — water is within limits')}")
        print(f"  {red(f'{c} critical')}  {yellow(f'{h} high')}  {cyan(f'{m} medium')}  {green(f'{l} low')}")

    print()
    for rec in rec_list:
        param    = rec.get("parameter", "--")
        priority = rec.get("priority", "--")
        urgency  = rec.get("urgency",  "--").replace("_", " ")
        treat    = rec.get("treatment", "--")

        print(f"  {_priority_fmt(priority):<22}  {cyan(bold(param))}")
        print(f"  {'Urgency':<22}  {yellow(urgency)}")
        lines = textwrap.wrap(treat, width=62)
        for i, line in enumerate(lines):
            prefix = "  Treatment" if i == 0 else "  " + " " * 10
            print(f"  {dim('Treatment'):<22}  {line}" if i == 0 else f"  {'':22}  {line}")
        print(dim("  " + "-" * 70))


def print_batch_summary(results: list, meta_list: list):
    section("BATCH SUMMARY")
    safe   = sum(1 for r in results if r.get("status") == "SAFE")
    nc     = sum(1 for r in results if r.get("status") == "NON_COMPLIANT")
    unsafe = sum(1 for r in results if r.get("status") == "UNSAFE")
    error  = sum(1 for r in results if r.get("status") == "ERROR")
    wqi_v  = [r["wqi"] for r in results if r.get("wqi") is not None]
    avg    = sum(wqi_v) / len(wqi_v) if wqi_v else None

    col("Total samples",   str(len(results)))
    col("Safe",            green(str(safe)))
    col("Non-compliant",   yellow(str(nc)))
    col("Unsafe",          red(str(unsafe)))
    if error:
        col("Errors",      red(str(error)))
    if avg is not None:
        col("Average WQI", cyan(f"{avg:.2f}"))
    print()

    print(f"  {'ID':<16} {'Location':<22} {'Status':<16} {'WQI':>6}  {'Classification'}")
    print(dim("  " + "-" * 80))
    for result, meta in zip(results, meta_list):
        sid  = str(meta.get("sample_id","--"))[:14]
        loc  = str(meta.get("location","--"))[:20]
        stat = result.get("status","--")
        wqi  = result.get("wqi")
        cls  = result.get("classification","--")
        wqi_s = f"{wqi:6.1f}" if wqi else "  N/A"
        print(f"  {cyan(sid):<25} {loc:<22} {_status_fmt(stat):<25} {wqi_s}  {dim(cls)}")


# ── PDF export ─────────────────────────────────────────────────────────────────

def offer_pdf(result: dict, recs: dict, meta: dict, default_name: str = ""):
    print()
    hr("EXPORT PDF REPORT")
    choice = _ask("Generate PDF report? (y/n)", default="y")
    if choice.lower() not in ("y", "yes"):
        return

    default_path = default_name or f"report_{meta.get('sample_id','sample')}.pdf"
    out_path = _ask("Output file path", default=default_path)

    try:
        from src.reports.generator import generate_pdf_report
        path = generate_pdf_report(
            wqi_result=result,
            recommendations=recs,
            output_path=out_path,
            meta=meta,
        )
        print(green(f"\n  Report saved: {bold(path)}"))
    except Exception as e:
        print(red(f"\n  PDF generation failed: {e}"))
        print(dim("  Make sure reportlab and matplotlib are installed."))


def offer_batch_pdf(results: list, recs: list, meta_list: list, title: str):
    print()
    hr("EXPORT BATCH PDF REPORT")
    choice = _ask("Generate batch PDF report? (y/n)", default="y")
    if choice.lower() not in ("y", "yes"):
        return

    out_path = _ask("Output file path", default="batch_report.pdf")
    try:
        from src.reports.generator import generate_batch_report
        path = generate_batch_report(
            results=results,
            rec_list=recs,
            output_path=out_path,
            meta_list=meta_list,
            batch_title=title,
        )
        print(green(f"\n  Batch report saved: {bold(path)}"))
    except Exception as e:
        print(red(f"\n  PDF generation failed: {e}"))
        print(dim("  Make sure reportlab and matplotlib are installed."))


# ── Single-sample flow ─────────────────────────────────────────────────────────

def run_single(profile_id: str = None, sample: dict = None,
               meta: dict = None, demo: bool = False):
    from src.engine.wqi_calculator import calculate_wqi
    from src.treatment.recommender import get_recommendations

    if not profile_id:
        profile_id, _ = select_profile()

    if demo:
        d = DEMO_SAMPLES.get(profile_id, list(DEMO_SAMPLES.values())[0])
        sample = d["sample"]
        meta   = {**d["meta"], "profile_id": profile_id,
                  "date": datetime.now().strftime("%d %b %Y")}
        print()
        print(cyan("  Using demo sample data:"))
        for k, v in sample.items():
            print(f"    {dim(k+':'):<22} {v}")
    elif sample is None:
        sample, meta = enter_sample_manually(profile_id)
    
    if not meta:
        meta = {"profile_id": profile_id, "date": datetime.now().strftime("%d %b %Y")}

    print()
    print(dim("  Running WQI engine..."))
    result = calculate_wqi(sample, profile_id)
    recs   = get_recommendations(wqi_result=result, profile_id=profile_id)

    print_result(result, meta, profile_id)
    print_recommendations(recs)
    offer_pdf(result, recs, meta)


# ── CSV batch flow ─────────────────────────────────────────────────────────────

def run_csv(profile_id: str = None, csv_path: str = None):
    from src.engine.wqi_calculator import calculate_wqi_from_csv
    from src.treatment.recommender import get_recommendations

    if not profile_id:
        profile_id, _ = select_profile()

    if not csv_path:
        csv_path = load_csv_path()

    print()
    print(dim(f"  Loading: {csv_path}"))
    results = calculate_wqi_from_csv(csv_path, profile_id)

    # Build meta list from result passthrough columns
    meta_list = []
    for r in results:
        meta_list.append({
            "sample_id":  r.get("sample_id", f"Row{len(meta_list)+1}"),
            "location":   r.get("location", "--"),
            "profile_id": profile_id,
            "date":       datetime.now().strftime("%d %b %Y"),
        })

    recs_list = [get_recommendations(wqi_result=r, profile_id=profile_id)
                 for r in results]

    print_batch_summary(results, meta_list)

    # Offer individual sample view
    print()
    while True:
        hr("INDIVIDUAL SAMPLE DETAIL")
        choice = _ask(
            "View a sample in detail? Enter Sample ID (or 'n' to skip)",
            default="n"
        )
        if choice.lower() in ("n", "no", ""):
            break
        found = False
        for i, (result, meta) in enumerate(zip(results, meta_list)):
            if str(meta.get("sample_id","")).lower() == choice.lower():
                print_result(result, meta, profile_id)
                print_recommendations(recs_list[i])
                found = True
                break
        if not found:
            ids = [str(m.get("sample_id","")) for m in meta_list]
            print(red(f"  Sample '{choice}' not found. Available: {', '.join(ids)}"))

    title = _ask("Batch report title",
                 default=f"Water Quality Survey — {datetime.now().strftime('%b %Y')}")
    offer_batch_pdf(results, recs_list, meta_list, title)


# ── Main menu ──────────────────────────────────────────────────────────────────

def main_menu():
    banner()
    opts = {
        "1": "Analyse a single sample  (enter values manually)",
        "2": "Analyse a CSV file       (batch mode)",
        "3": "Run demo sample          (see a quick example)",
        "4": "Exit",
    }
    choice = _choose("What would you like to do?", opts)

    if choice == "1":
        run_single()
    elif choice == "2":
        run_csv()
    elif choice == "3":
        pid, _ = select_profile()
        run_single(profile_id=pid, demo=True)
    elif choice == "4":
        print(dim("\n  Goodbye.\n"))
        raise SystemExit(0)


# ── CLI entry point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="python main.py",
        description="Project UPD — Water Quality Index System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python main.py                          # interactive menu
          python main.py --demo                   # quick demo (BIS drinking)
          python main.py --demo --profile 3       # demo with FAO agriculture profile
          python main.py --sample                 # manual single-sample entry
          python main.py --csv data/samples/sample_input.csv
          python main.py --csv mydata.csv --profile 2 --out reports/batch.pdf
        """),
    )
    parser.add_argument("--sample",  action="store_true",
                        help="Enter a single sample manually")
    parser.add_argument("--csv",     metavar="FILE",
                        help="Analyse all samples in a CSV file")
    parser.add_argument("--demo",    action="store_true",
                        help="Run a built-in demo sample")
    parser.add_argument("--profile", metavar="N",  default=None,
                        choices=["1","2","3","4","5"],
                        help="Profile: 1=BIS 2=WHO 3=FAO 4=Aquaculture 5=Industrial")
    parser.add_argument("--out",     metavar="PDF",
                        help="Auto-save PDF to this path (skips prompt)")

    args = parser.parse_args()

    # Resolve profile
    profile_id = None
    if args.profile:
        profile_id = PROFILES[args.profile][0]

    try:
        if args.demo:
            banner()
            pid = profile_id or PROFILES["1"][0]
            run_single(profile_id=pid, demo=True)

        elif args.sample:
            banner()
            run_single(profile_id=profile_id)

        elif args.csv:
            banner()
            run_csv(profile_id=profile_id, csv_path=args.csv)

        else:
            # Interactive menu
            while True:
                main_menu()
                print()
                again = _ask("Run another analysis? (y/n)", default="y")
                if again.lower() not in ("y", "yes"):
                    break
            print(dim("\n  Goodbye.\n"))

    except KeyboardInterrupt:
        print(dim("\n\n  Interrupted. Goodbye.\n"))
        raise SystemExit(0)


if __name__ == "__main__":
    main()