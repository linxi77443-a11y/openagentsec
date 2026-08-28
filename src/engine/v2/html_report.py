"""4-View Offline HTML Report Generator (Phase 113A VIEW-013)
Path: src/engine/v2/html_report.py

Renders a fully offline, self-contained HTML report (no external links,
no external scripts, all samples HTML-escaped) from a JSON full report.

Safety boundaries:
- synthetic_only: True
- confirmed_vulnerability: False
- formal_finding_allowed: False
- report is NOT an execution interface
"""

import html
import json
from typing import Any, Dict, List

from src.engine.v2.safety_invariants import assert_safety_invariants

SAFETY_DECLARATION = (
    "synthetic_only | requires_human_review | This is NOT an execution interface."
)

_STYLE = """    <style>
        body { font-family: sans-serif; margin: 20px; }
        h1, h2, h3 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 0.9em; color: #666; }
    </style>"""


def _escape(text: Any) -> str:
    """HTML-escapes a value for safe inline rendering (no quotes escaping)."""
    return html.escape(str(text), quote=False)


def _render_overview(data: Dict[str, Any]) -> str:
    metrics = data.get("baseline_metrics", {})
    modules = data.get("modules_covered", [])
    return f"""    <div id="overview">
        <h2>1. Overview Scorecard</h2>
        <p>Modules Covered: {_escape(', '.join(modules))}</p>
        <ul>
            <li>Precision: {metrics.get('precision', '')}</li>
            <li>Recall: {metrics.get('recall', '')}</li>
            <li>F1: {metrics.get('f1', '')}</li>
            <li>Benign Correctness: {metrics.get('benign_correctness', '')}</li>
        </ul>
    </div>"""


def _render_matrix(data: Dict[str, Any]) -> str:
    rows = data.get("technique_intent_matrix", [])
    row_html = "".join(
        f"<tr><td>{_escape(r.get('technique', ''))}</td>"
        f"<td>{_escape(r.get('intent', ''))}</td>"
        f"<td>{_escape(r.get('coverage', ''))}</td></tr>"
        for r in rows
    )
    return f"""    <div id="matrix">
        <h2>2. Technique x Intent Coverage Matrix</h2>
        <table border="1">
            <tr><th>Technique</th><th>Intent</th><th>Coverage</th></tr>
            {row_html}
        </table>
    </div>"""


def _render_calibration(data: Dict[str, Any]) -> str:
    cm = data.get("m25_calibration", {}).get("confusion_matrix", {})
    return f"""    <div id="calibration">
        <h2>3. M25 Calibration View</h2>
        <table border="1">
            <tr><th>TP</th><th>FP</th><th>TN</th><th>FN</th></tr>
            <tr>
                <td>{cm.get('tp', '')}</td>
                <td>{cm.get('fp', '')}</td>
                <td>{cm.get('tn', '')}</td>
                <td>{cm.get('fn', '')}</td>
            </tr>
        </table>
    </div>"""


def _render_risk(data: Dict[str, Any]) -> str:
    risk = data.get("residual_risk", {})
    return f"""    <div id="risk">
        <h2>4. Adaptive Residual Risk</h2>
        <ul>
            <li>Static Risk: {risk.get('static', '')}</li>
            <li>Adaptive Risk: {risk.get('adaptive', '')}</li>
            <li>Acknowledged: {risk.get('acknowledged', '')}</li>
        </ul>
    </div>"""


def _render_samples(data: Dict[str, Any]) -> str:
    samples: List[Dict[str, Any]] = data.get("samples", [])
    items = "".join(
        f"<li>{_escape(s.get('id', ''))}: {_escape(s.get('text', ''))}</li>"
        for s in samples
    )
    return f"""    <h3>Samples</h3><ul>{items}</ul>"""


def generate_html_report(json_path: str) -> str:
    """Reads a JSON full report and renders the offline 4-view HTML report."""
    assert_safety_invariants()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    parts = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '    <title>Offline HTML Report</title>',
        _STYLE,
        "</head>",
        "<body>",
        "    <h1>Security Assessment Report</h1>",
        "    <nav>",
        "        <ul>",
        '            <li><a href="#overview">1. Overview Scorecard</a></li>',
        '            <li><a href="#matrix">2. Coverage Matrix</a></li>',
        '            <li><a href="#calibration">3. Calibration</a></li>',
        '            <li><a href="#risk">4. Residual Risk</a></li>',
        "        </ul>",
        "    </nav>",
        "    ",
        "    ",
        _render_overview(data),
        "    ",
        "    ",
        _render_matrix(data),
        "    ",
        "    ",
        _render_calibration(data),
        "    ",
        "    ",
        _render_risk(data),
        "    ",
        _render_samples(data),
        "    ",
        '    <div class="footer">',
        f"        <p><strong>SAFETY DECLARATION:</strong> {SAFETY_DECLARATION}</p>",
        "    </div>",
        "</body>",
        "</html>",
    ]
    return "\n".join(parts) + "\n"
