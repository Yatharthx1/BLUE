"""
api_client.py — Phase 5 Placeholder
LLM integration for natural language water quality explanations.
Supports OpenAI, Anthropic, Gemini via env config.
"""

import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "openai")


def explain_wqi_result(wqi_result: dict, recommendations: list) -> str:
    """
    Send WQI result to LLM and get a plain-language explanation.
    Phase 5 implementation.
    """
    raise NotImplementedError("LLM client not yet implemented. Coming in Phase 5.")

# TODO Phase 5:
# - Build prompt template with WQI result + recommendations
# - Call provider API
# - Return explanation string for use in reports
