"""Shared refusal signal loader — single source of truth for all assessment scripts.

Loads refusal signals and breakthrough keywords from rules/refusal_signals.yaml.
All three runners (run_local_hermes_assessment.py, run_internal_security_assessment.py,
build_internal_assessment_report.py) MUST use this module instead of maintaining
duplicate lists.

Usage:
    from shared_refusal import load_refusal_signals, is_refusal, load_breakthrough_keywords

    signals = load_refusal_signals()
    if is_refusal(response_text):
        # classify as correctly_refused / properly_blocked

    bt_keywords = load_breakthrough_keywords()
"""

import os
import yaml
from pathlib import Path

_REFUSAL_SIGNALS = None
_BREAKTHROUGH_KEYWORDS = None
_RULES_PATH = None


def _get_rules_path():
    """Find rules/refusal_signals.yaml relative to this file or the project root."""
    global _RULES_PATH
    if _RULES_PATH:
        return _RULES_PATH
    # Relative to this file
    candidate = Path(__file__).resolve().parent.parent / "rules" / "refusal_signals.yaml"
    if candidate.exists():
        _RULES_PATH = candidate
        return _RULES_PATH
    # Relative to CWD (project root)
    candidate2 = Path("rules") / "refusal_signals.yaml"
    if candidate2.exists():
        _RULES_PATH = candidate2
        return _RULES_PATH
    raise FileNotFoundError(
        "rules/refusal_signals.yaml not found. "
        "Run from project root or ensure the file exists."
    )


def load_refusal_signals(force_reload=False):
    """Load refusal signal patterns from shared YAML file (cached).

    Returns:
        list[str]: Refusal signal patterns to match against response text.
    """
    global _REFUSAL_SIGNALS
    if _REFUSAL_SIGNALS is not None and not force_reload:
        return _REFUSAL_SIGNALS
    path = _get_rules_path()
    with open(path) as f:
        data = yaml.safe_load(f)
    _REFUSAL_SIGNALS = data.get("refusal_signal_patterns", [])
    return _REFUSAL_SIGNALS


def load_breakthrough_keywords(force_reload=False):
    """Load breakthrough trigger keywords from shared YAML file (cached).

    Returns:
        list[str]: Breakthrough trigger keywords.
    """
    global _BREAKTHROUGH_KEYWORDS
    if _BREAKTHROUGH_KEYWORDS is not None and not force_reload:
        return _BREAKTHROUGH_KEYWORDS
    path = _get_rules_path()
    with open(path) as f:
        data = yaml.safe_load(f)
    _BREAKTHROUGH_KEYWORDS = data.get("breakthrough_trigger_keywords", [])
    return _BREAKTHROUGH_KEYWORDS


def is_refusal(response_text):
    """Check if response text contains any refusal signal.

    Per PRD §11.2/§17.1 and parser_regression_guard.yaml:
    Refusal signals take priority over breakthrough keywords.
    If matched, the response MUST be classified as correctly_refused
    or properly_blocked, NOT as breakthrough_suspected.

    Args:
        response_text: The model's response text to check.

    Returns:
        bool: True if a refusal signal is found.
    """
    if not response_text:
        return False
    text_lower = response_text.lower()[:500]
    signals = load_refusal_signals()
    return any(sig.lower() in text_lower for sig in signals)
