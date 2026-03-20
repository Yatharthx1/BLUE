# Project UPD — Water Quality Index Engine

A modular Python system for computing WQI, recommending water treatments,
and generating reports — with ML and LLM integration planned.

## Phases
1. **WQI Engine** — Weighted parameter scoring (BIS + WHO standards)
2. **Standards Layer** — Pluggable multi-standard support
3. **Treatment Recommender** — Rule-based + ML-driven suggestions
4. **LLM Integration** — Natural language explanations via API
5. **ReportLab** — Auto-generated PDF water quality reports

## Setup
\\\ash
pip install -r requirements.txt
jupyter notebook notebooks/
\\\
"@

Write-ProjectFile "requirements.txt" @"
# Core
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.11.0

# Notebooks
jupyter>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0

# ML (Phase 4)
scikit-learn>=1.3.0
# torch>=2.0.0  # Uncomment when needed

# LLM API (Phase 5)
openai>=1.0.0          # or swap with anthropic / google-generativeai
python-dotenv>=1.0.0

# Reports (Phase 6)
reportlab>=4.0.0

# Utilities
pydantic>=2.0.0
loguru>=0.7.0
