#!/usr/bin/env python3
"""Phase 35 — Build Promptfoo Integration Framework.

Reads existing promptfoo drafts from:
  - generated_testcases/chatbot/promptfoo_chatbot_generated.yaml
  - generated_testcases/agent/promptfoo_agent_generated.yaml
  - generated_testcases/rag/promptfoo_rag_generated.yaml
  - generated_testcases/api/promptfoo_api_generated.yaml
  - generated_testcases/regression/promptfoo_regression_generated.yaml

And regression suites from:
  - regression_suites/promptfoo_drafts/promptfoo_chatbot_regression.yaml
  - regression_suites/promptfoo_drafts/promptfoo_agent_regression.yaml
  - regression_suites/promptfoo_drafts/promptfoo_rag_regression.yaml
  - regression_suites/promptfoo_drafts/promptfoo_api_regression.yaml
  - regression_suites/promptfoo_drafts/promptfoo_owasp_agentic_regression.yaml
  - regression_suites/promptfoo_drafts/promptfoo_owasp_llm_regression.yaml
  - regression_suites/promptfoo_drafts/promptfoo_core_llm_regression.yaml

And generates:
  - tool_integrations/promptfoo/promptfoo_config_index.yaml
    (if not already populated, generates it from discovered files)
  - Validates that all promptfoo drafts have correct security flags
  - Prints summary of discovered drafts and suites

Security constraints:
  - No running promptfoo eval
  - No connecting target API
  - No calling DeepSeek API
  - No reading .local/
  - No modifying original drafts
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# I/O paths
# ---------------------------------------------------------------------------

# Generated testcase promptfoo drafts
GENERATED_DIRS: Dict[str, Path] = {
    "chatbot": ROOT / "generated_testcases" / "chatbot" / "promptfoo_chatbot_generated.yaml",
    "agent": ROOT / "generated_testcases" / "agent" / "promptfoo_agent_generated.yaml",
    "rag": ROOT / "generated_testcases" / "rag" / "promptfoo_rag_generated.yaml",
    "api": ROOT / "generated_testcases" / "api" / "promptfoo_api_generated.yaml",
    "regression": ROOT / "generated_testcases" / "regression" / "promptfoo_regression_generated.yaml",
}

# Regression suite promptfoo drafts
REGRESSION_DRAFTS: Dict[str, Path] = {
    "chatbot_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_chatbot_regression.yaml",
    "agent_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_agent_regression.yaml",
    "rag_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_rag_regression.yaml",
    "api_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_api_regression.yaml",
    "owasp_agentic_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_owasp_agentic_regression.yaml",
    "owasp_llm_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_owasp_llm_regression.yaml",
    "core_llm_regression": ROOT / "regression_suites" / "promptfoo_drafts" / "promptfoo_core_llm_regression.yaml",
}

# Output paths
INTEGRATION_DIR = ROOT / "tool_integrations" / "promptfoo"
CONFIG_INDEX_PATH = INTEGRATION_DIR / "promptfoo_config_index.yaml"

EXPECTED_SECURITY_FLAGS: Dict[str, bool] = {
    "executed": False,
    "real_target_connected": False,
    "usable_for_formal_finding": False,
}

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------


def load_yaml(path: Path) -> dict:
    """Load a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def count_tests(data: dict) -> int:
    """Count test entries in a promptfoo draft."""
    tests = data.get("tests", [])
    if tests is None:
        return 0
    return len(tests)


def check_security_flags(
    data: dict, label: str, strict: bool = True
) -> Tuple[int, int, List[str]]:
    """Check security flags on a promptfoo draft.

    Returns (passed, failed, failure_messages).
    """
    passed = 0
    failed = 0
    failures: List[str] = []

    for flag, expected in EXPECTED_SECURITY_FLAGS.items():
        actual = data.get(flag)
        if actual is None:
            msg = f"[{label}] Missing security flag '{flag}'"
            failures.append(msg)
            failed += 1
        elif actual != expected:
            msg = (
                f"[{label}] Security flag '{flag}' expected={expected}, "
                f"actual={actual}"
            )
            failures.append(msg)
            failed += 1
        else:
            passed += 1

    # Also check top-level flags
    generated_only = data.get("generated_only")
    if generated_only is None:
        failures.append(f"[{label}] Missing top-level flag 'generated_only'")
        failed += 1
    elif generated_only is not True:
        failures.append(f"[{label}] 'generated_only' expected=True, actual={generated_only}")
        failed += 1
    else:
        passed += 1

    return passed, failed, failures


def check_metadata_security_flags(
    data: dict, label: str
) -> Tuple[int, int, List[str]]:
    """Check security flags in every test's metadata section."""
    passed = 0
    failed = 0
    failures: List[str] = []

    tests = data.get("tests", [])
    if not tests:
        return passed, failed, failures

    for i, test in enumerate(tests):
        meta = test.get("metadata", {})
        for flag in ("executed", "real_target_connected", "usable_for_formal_finding"):
            val = meta.get(flag)
            if val is None:
                failures.append(
                    f"[{label}] Test #{i} metadata missing '{flag}'"
                )
                failed += 1
            elif val is not False:
                failures.append(
                    f"[{label}] Test #{i} metadata '{flag}' expected=False, "
                    f"actual={val}"
                )
                failed += 1
            else:
                passed += 1

    return passed, failed, failures


def build_profile_entry(
    profile_name: str,
    draft_path: Path,
    data: dict,
    draft_type: str,
) -> dict:
    """Build a config index entry for a discovered draft."""
    test_count = count_tests(data)
    return {
        "profile": profile_name,
        "source_path": str(draft_path.relative_to(ROOT)),
        "draft_type": draft_type,
        "target": data.get("target", "unknown"),
        "test_count": test_count,
        "generated_only": data.get("generated_only", True),
        "executed": data.get("executed", False),
        "real_target_connected": data.get("real_target_connected", False),
        "usable_for_formal_finding": data.get("usable_for_formal_finding", False),
        "generated_at": data.get("generated_at", "unknown"),
        "discovered_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Build functions
# ---------------------------------------------------------------------------


def discover_generated_drafts() -> List[Dict]:
    """Discover and parse all generated testcase promptfoo drafts."""
    entries: List[Dict] = []
    for profile_name, path in GENERATED_DIRS.items():
        if not path.exists():
            print(f"  [SKIP] Generated draft not found: {path}")
            continue
        data = load_yaml(path)
        entry = build_profile_entry(
            profile_name=profile_name,
            draft_path=path,
            data=data,
            draft_type="generated_testcase",
        )
        entries.append(entry)
    return entries


def discover_regression_drafts() -> List[Dict]:
    """Discover and parse all regression suite promptfoo drafts."""
    entries: List[Dict] = []
    for suite_name, path in REGRESSION_DRAFTS.items():
        if not path.exists():
            print(f"  [SKIP] Regression draft not found: {path}")
            continue
        data = load_yaml(path)
        entry = build_profile_entry(
            profile_name=suite_name,
            draft_path=path,
            data=data,
            draft_type="regression_suite",
        )
        # Add suite-specific fields
        entry["suite_id"] = data.get("suite_id", "unknown")
        entry["suite_name"] = data.get("suite_name", "unknown")
        entry["target_profiles"] = data.get("target_profiles", [])
        entry["curated_from_static_analysis"] = data.get(
            "curated_from_static_analysis", False
        )
        entries.append(entry)
    return entries


def generate_config_index(
    generated_entries: List[Dict],
    regression_entries: List[Dict],
) -> dict:
    """Generate the promptfoo_config_index.yaml content."""
    return {
        "config_index": {
            "tool": "promptfoo",
            "version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "scripts/build_promptfoo_integration_framework.py",
            "security_boundaries": {
                "promptfoo_eval_run": False,
                "target_api_connected": False,
                "deepseek_api_called": False,
                "local_config_read": False,
                "original_drafts_modified": False,
            },
        },
        "generated_testcase_profiles": generated_entries,
        "regression_suite_profiles": regression_entries,
        "summary": {
            "total_generated_drafts": len(generated_entries),
            "total_regression_drafts": len(regression_entries),
            "total_drafts": len(generated_entries) + len(regression_entries),
        },
    }


def validate_all_security_flags(
    generated_entries: List[Dict],
    regression_entries: List[Dict],
) -> Tuple[int, int, List[str]]:
    """Validate security flags on all discovered drafts.

    Returns (total_passed, total_failed, all_failures).
    """
    total_passed = 0
    total_failed = 0
    all_failures: List[str] = []

    # Validate generated drafts
    for entry in generated_entries:
        profile = entry["profile"]
        path = ROOT / entry["source_path"]
        data = load_yaml(path)

        p, f, msgs = check_security_flags(data, f"generated/{profile}")
        total_passed += p
        total_failed += f
        all_failures.extend(msgs)

        p, f, msgs = check_metadata_security_flags(
            data, f"generated/{profile}"
        )
        total_passed += p
        total_failed += f
        all_failures.extend(msgs)

    # Validate regression drafts
    for entry in regression_entries:
        profile = entry["profile"]
        path = ROOT / entry["source_path"]
        data = load_yaml(path)

        p, f, msgs = check_security_flags(data, f"regression/{profile}")
        total_passed += p
        total_failed += f
        all_failures.extend(msgs)

        p, f, msgs = check_metadata_security_flags(
            data, f"regression/{profile}"
        )
        total_passed += p
        total_failed += f
        all_failures.extend(msgs)

    return total_passed, total_failed, all_failures


def print_summary(
    generated_entries: List[Dict],
    regression_entries: List[Dict],
    validation_passed: int,
    validation_failed: int,
    failures: List[str],
    config_index: dict,
) -> None:
    """Print a human-readable summary of discovered drafts and suites."""
    summary = config_index["summary"]

    print()
    print("=" * 70)
    print("  Promptfoo Integration Framework — Build Summary")
    print("=" * 70)
    print()
    print(f"  Generated testcase drafts:   {summary['total_generated_drafts']}")
    print(f"  Regression suite drafts:     {summary['total_regression_drafts']}")
    print(f"  Total drafts:                {summary['total_drafts']}")
    print()

    if generated_entries:
        print("  --- Generated Testcase Profiles ---")
        for e in generated_entries:
            print(
                f"    {e['profile']:20s}  target={e['target']:15s}  "
                f"tests={e['test_count']:4d}  source={e['source_path']}"
            )

    if regression_entries:
        print()
        print("  --- Regression Suite Profiles ---")
        for e in regression_entries:
            profiles = ",".join(e["target_profiles"])
            print(
                f"    {e['profile']:25s}  targets={profiles:20s}  "
                f"tests={e['test_count']:4d}  source={e['source_path']}"
            )

    print()
    print("  --- Security Flag Validation ---")
    print(f"    Checks passed: {validation_passed}")
    print(f"    Checks failed: {validation_failed}")
    if failures:
        print("    Failures:")
        for f in failures:
            print(f"      - {f}")
    else:
        print("    All security flags correct.")

    print()
    print("  --- Generated Output ---")
    print(f"    {CONFIG_INDEX_PATH.relative_to(ROOT)}")
    print()

    if validation_failed > 0:
        print("  [WARNING] Security flag validation has failures.")
        print("  The config index was still generated, but drafts need review.")
    else:
        print("  [OK] All validations passed.")

    print("=" * 70)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("=" * 70)
    print("Phase 35 — Build Promptfoo Integration Framework")
    print("=" * 70)

    # Ensure integration directory exists
    INTEGRATION_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Discover generated testcase drafts
    print("\n[1/4] Discovering generated testcase promptfoo drafts...")
    generated_entries = discover_generated_drafts()
    for e in generated_entries:
        print(f"  [OK] {e['profile']:20s} ({e['test_count']} tests)")

    # 2. Discover regression suite drafts
    print("\n[2/4] Discovering regression suite promptfoo drafts...")
    regression_entries = discover_regression_drafts()
    for e in regression_entries:
        print(f"  [OK] {e['profile']:25s} ({e['test_count']} tests)")

    # 3. Validate security flags on all drafts
    print("\n[3/4] Validating security flags on all drafts...")
    validation_passed, validation_failed, failures = validate_all_security_flags(
        generated_entries, regression_entries
    )
    print(f"  Checks passed: {validation_passed}")
    print(f"  Checks failed: {validation_failed}")

    # 4. Generate config index
    print("\n[4/4] Generating promptfoo config index...")
    config_index = generate_config_index(generated_entries, regression_entries)

    # Check if config index already exists and is populated
    if CONFIG_INDEX_PATH.exists():
        existing = load_yaml(CONFIG_INDEX_PATH)
        existing_profiles = existing.get("config_index", {}).get("profiles", [])
        if existing_profiles:
            print("  Config index already populated — overwriting with fresh discovery.")
        else:
            print("  Config index exists but empty — generating from discovered files.")

    with open(CONFIG_INDEX_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config_index, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  [OK] {CONFIG_INDEX_PATH}")

    # Print summary
    print_summary(
        generated_entries=generated_entries,
        regression_entries=regression_entries,
        validation_passed=validation_passed,
        validation_failed=validation_failed,
        failures=failures,
        config_index=config_index,
    )

    print()
    print("Phase 35 build complete — no promptfoo eval run, no target API connected,")
    print("no DeepSeek API called, no .local/ read, no original drafts modified.")
    print()

    # Always return 0 — validation is informational. The validate script gates.
    return 0


if __name__ == "__main__":
    sys.exit(main())
