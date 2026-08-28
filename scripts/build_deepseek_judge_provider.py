#!/usr/bin/env python3
"""Build Phase 34A DeepSeek Judge Provider Framework.

Generates provider template, schema, prompt templates, mock results, and
adapter skeleton for the DeepSeek Judge Provider. All outputs are mock-only —
no real API calls, no credential access, no network execution.

No network calls, no credential access, no API execution.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML required: pip install pyyaml") from exc

ROOT = Path(__file__).resolve().parents[1]
JPD_DIR = ROOT / "tool_judge_providers"
DS_DIR = JPD_DIR / "deepseek"
MOCK_DIR = DS_DIR / "mock_outputs"
ADAPTER_DIR = DS_DIR / "adapter"

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f+00:00")

# ── Provider identity ───────────────────────────────────────────────────

PROVIDER_ID = "JPD-001"
PROVIDER_NAME = "deepseek_judge_provider"
JUDGE_MODEL = "deepseek-chat"
JUDGE_MODE = "mock_only"
MAX_JUDGE_CALLS = 16

USE_CASES = [
    "finding_candidate_triage",
    "system_prompt_leakage_review",
    "sensitive_disclosure_review",
    "rag_boundary_review",
    "prompt_injection_bypass_review",
    "api_boundary_review",
    "retest_result_review",
    "tool_result_review",
]

# ── Finding group definitions (mirrors Phase 33 GROUPS) ─────────────────

GROUPS: dict[str, dict[str, Any]] = {
    "system_prompt_leakage": {
        "risk_category": "C03",
        "severity": "Critical",
        "candidate_count": 4,
        "candidates": [
            "FC-32C-gtc_chatbot-spe-001",
            "FC-32C-gtc_chatbot-spe-002",
            "FC-32C-gtc_chatbot-spe-003",
            "FC-32C-gtc_regression-cs-002",
        ],
    },
    "sensitive_disclosure": {
        "risk_category": "C04",
        "severity": "Critical",
        "candidate_count": 4,
        "candidates": [
            "FC-32C-gtc_chatbot-sd-001",
            "FC-32C-gtc_chatbot-sd-002",
            "FC-32C-gtc_chatbot-sd-004",
            "FC-32C-gtc_regression-cs-003",
        ],
    },
    "rag_exposure": {
        "risk_category": "C09",
        "severity": "Critical",
        "candidate_count": 2,
        "candidates": [
            "FC-32C-rag-001",
            "FC-32C-rag-002",
        ],
    },
    "prompt_injection_bypass": {
        "risk_category": "C02",
        "severity": "High",
        "candidate_count": 4,
        "candidates": [
            "FC-32C-gtc_chatbot-pi-004",
            "FC-32C-gtc_chatbot-mb-001",
            "FC-32C-gtc_chatbot-mb-002",
            "FC-32C-gtc_chatbot-mb-003",
        ],
    },
    "api_boundary_weakness": {
        "risk_category": "C07",
        "severity": "Critical",
        "candidate_count": 2,
        "candidates": [
            "FC-32C-gtc_api-asb-001",
            "FC-32C-gtc_api-asb-002",
        ],
    },
}


# ── File checks ─────────────────────────────────────────────────────────

def check_file(path: Path, label: str) -> bool:
    exists = path.exists()
    if not exists:
        print(f"  [MISSING] {label}: {path.name}")
    else:
        print(f"  [OK]      {label}: {path.name}")
    return exists


def build_judge_provider_index() -> dict[str, Any]:
    """Build the judge provider index YAML."""
    return {
        "judge_provider_index": {
            "source_phase": "Phase 34A",
            "created_at": NOW,
            "status": "framework_ready",
            "judge_mode": JUDGE_MODE,
            "network_called": False,
            "credential_loaded": False,
            "usable_for_formal_finding": False,
            "human_go_no_go_required": True,
            "total_providers": 1,
            "total_use_cases": len(USE_CASES),
            "providers": [
                {
                    "provider_id": PROVIDER_ID,
                    "provider_name": PROVIDER_NAME,
                    "judge_model": JUDGE_MODEL,
                    "judge_mode": JUDGE_MODE,
                    "network_allowed": False,
                    "execution_allowed": False,
                    "credential_source": ".local/deepseek_judge_provider.local.yaml",
                    "max_judge_calls": MAX_JUDGE_CALLS,
                    "cost_guard_enabled": True,
                    "human_go_no_go_required": True,
                    "supported_use_cases": USE_CASES,
                    "directory": "deepseek/",
                }
            ],
        }
    }


def build_judge_provider_boundary() -> str:
    """Build the judge provider boundary markdown."""
    lines = [
        "# Judge Provider Boundary / 判官提供者边界\n",
        "## Current Boundary / 当前边界\n",
        "| Constraint | Value |",
        "|------------|-------|",
        "| network_called | false |",
        "| credential_loaded | false |",
        "| real_api_connected | false |",
        "| judge_mode | mock_only |",
        "| execution_allowed | false |",
        "| max_judge_calls | 16 (default) |",
        "| cost_guard_enabled | true |",
        "| human_go_no_go_required | true |",
        "| usable_for_formal_finding | false |",
        "| formal_finding | false |",
        "| formal_customer_report | false |",
        "",
        "## Currently Allowed / 当前允许",
        "",
        "- Judge provider schema definition",
        "- Provider template generation (placeholders only)",
        "- Judge prompt template definition",
        "- Judge schema definition",
        "- Mock judge result generation (no real API calls)",
        "- Adapter skeleton creation (stub methods only)",
        "- Static validation (no network, no credentials)",
        "- Build and refresh scripts (no API calls)",
        "- Validation scripts (static checks only)",
        "",
        "## Currently Prohibited / 当前禁止",
        "",
        '- ❌ Reading `.local/` credentials',
        "- ❌ Connecting to DeepSeek API",
        "- ❌ Connecting to any real API",
        "- ❌ Re-running Phase 32C API tests",
        "- ❌ Running promptfoo eval",
        "- ❌ Running garak / PyRIT",
        "- ❌ Running curl / wget",
        "- ❌ Generating real judge conclusions",
        "- ❌ Marking finding candidates as validated",
        "- ❌ Generating formal vulnerability conclusions",
        "- ❌ Generating formal customer reports",
        '- ❌ Including API keys, Authorization headers, or unredacted endpoints in output',
        "",
    ]
    return "\n".join(lines)


def verify() -> bool:
    """Verify all expected files exist."""
    print(f"\n{'='*60}")
    print("Phase 34A File Verification")
    print(f"{'='*60}")

    all_ok = True

    # Top-level files
    top_files = [
        (JPD_DIR / "README.md", "JPD README"),
        (JPD_DIR / "judge_provider_schema.md", "JPD Schema"),
        (JPD_DIR / "judge_provider_index.yaml", "JPD Index"),
        (JPD_DIR / "judge_provider_boundary.md", "JPD Boundary"),
    ]
    for path, label in top_files:
        all_ok &= check_file(path, label)

    # DeepSeek subdirectory
    ds_files = [
        (DS_DIR / "README.md", "DS README"),
        (DS_DIR / "deepseek_judge_provider.template.yaml", "DS Template"),
        (DS_DIR / "deepseek_judge_prompt_templates.yaml", "DS Prompt Templates"),
        (DS_DIR / "deepseek_judge_schema.yaml", "DS Schema"),
        (DS_DIR / "deepseek_judge_mock_results.yaml", "DS Mock Results"),
        (DS_DIR / "deepseek_judge_boundary.md", "DS Boundary"),
    ]
    for path, label in ds_files:
        all_ok &= check_file(path, label)

    # Mock outputs
    mock_files = [
        (MOCK_DIR / "finding_candidate_judge_results.yaml", "Mock: Candidate Results"),
        (MOCK_DIR / "consolidated_group_judge_results.yaml", "Mock: Group Results"),
        (MOCK_DIR / "judge_summary.md", "Mock: Summary"),
    ]
    for path, label in mock_files:
        all_ok &= check_file(path, label)

    # Adapter
    adapter_files = [
        (ADAPTER_DIR / "README.md", "Adapter README"),
        (ADAPTER_DIR / "deepseek_judge_adapter.py", "Adapter Python"),
    ]
    for path, label in adapter_files:
        all_ok &= check_file(path, label)

    print(f"\n{'='*60}")
    if all_ok:
        print("All Phase 34A files verified OK.")
    else:
        print("Some Phase 34A files are MISSING.")
    print(f"{'='*60}")
    return all_ok


def main() -> None:
    print(f"Phase 34A Build — DeepSeek Judge Provider Framework")
    print(f"Generated: {NOW}")
    print(f"Mode: {JUDGE_MODE}")
    print(f"Use Cases: {len(USE_CASES)}")
    print(f"Finding Groups: {len(GROUPS)}")

    # Verify all files
    ok = verify()

    # Build index (in-memory check — file already written by template)
    index = build_judge_provider_index()
    print(f"\nIndex provider count: {len(index['judge_provider_index']['providers'])}")
    print(f"Index use case count: {index['judge_provider_index']['total_use_cases']}")

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
