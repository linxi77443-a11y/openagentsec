#!/usr/bin/env python3
"""Phase-aware Validator for the Phase-PATCH-FLOW-003 synthetic planning/delivery assets.

Supports three phases:
  --phase planning: checks planning assets only (generated_manifest.yaml not required)
  --phase development: checks that generated_manifest.yaml matches source (intentional issue present)
  --phase patch: checks that generated_manifest.yaml matches expected (issue fixed)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "workflow_test_fixtures" / "patch_flow_003"
EXPECTED_PATH = FIXTURE_DIR / "expected_manifest.yaml"
SOURCE_PATH = FIXTURE_DIR / "source_manifest.yaml"
GENERATED_PATH = FIXTURE_DIR / "generated_manifest.yaml"
TASK_PACKAGE_PATH = ROOT / "task_packages" / "Phase-PATCH-FLOW-003" / "task_package.yaml"
BATCH_MANIFEST_PATH = ROOT / "runtime" / "BATCH-2026-07-20-007" / "batch_manifest.yaml"
PLANNING_FREEZE_PATH = ROOT / "runtime" / "BATCH-2026-07-20-007" / "planning_freeze.yaml"


def load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML top level must be a mapping: {path}")
    return value


def check_planning_assets() -> list[str]:
    """PL-01: Check planning assets exist."""
    failures = []
    planning_paths = [
        EXPECTED_PATH,
        SOURCE_PATH,
        TASK_PACKAGE_PATH,
        BATCH_MANIFEST_PATH,
        PLANNING_FREEZE_PATH,
    ]
    missing = [str(path.relative_to(ROOT)) for path in planning_paths if not path.is_file()]
    if missing:
        failures.append(f"PL-01 missing planning assets: {missing}")
    return failures


def check_fixture_structure() -> tuple[list[str], dict, dict]:
    """PL-02, PL-03: Check fixture structure and synthetic_workflow_version."""
    failures = []
    expected = {}
    source = {}

    try:
        expected = load_mapping(EXPECTED_PATH)
        source = load_mapping(SOURCE_PATH)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        failures.append(f"PL-02 Fixture YAML invalid: {exc}")
        return failures, expected, source

    if expected.get("synthetic_workflow_version") != "v0.1.0":
        failures.append("PL-03 expected Fixture must define synthetic_workflow_version: v0.1.0")
    if "synthetic_workflow_version" in source:
        failures.append("PL-03 source Fixture must omit synthetic_workflow_version for the intended review issue")

    return failures, expected, source


def check_safety_fields(expected: dict, source: dict) -> list[str]:
    """PL-05: Check safety fields."""
    failures = []
    for label, value in (("expected", expected), ("source", source)):
        if value.get("synthetic_only") is not True:
            failures.append(f"PL-05 {label} Fixture must set synthetic_only: true")
        if value.get("real_data_used") is not False:
            failures.append(f"PL-05 {label} Fixture must set real_data_used: false")
        if value.get("external_targets_allowed") is not False:
            failures.append(f"PL-05 {label} Fixture must set external_targets_allowed: false")
    return failures


def check_development_phase() -> list[str]:
    """Development phase: generated matches source, differs from expected."""
    failures = []

    if not GENERATED_PATH.exists():
        failures.append("DEV-01 generated_manifest.yaml must exist during development phase")
        return failures

    try:
        generated = load_mapping(GENERATED_PATH)
        source = load_mapping(SOURCE_PATH)
        expected = load_mapping(EXPECTED_PATH)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        failures.append(f"DEV-02 Fixture YAML invalid: {exc}")
        return failures

    if generated != source:
        failures.append("DEV-03 generated Fixture must match source during development (issue present)")

    if generated == expected:
        failures.append("DEV-04 generated Fixture must differ from expected during development (issue not yet fixed)")

    if "synthetic_workflow_version" in generated:
        failures.append("DEV-05 generated Fixture must omit synthetic_workflow_version during development")

    return failures


def check_patch_phase() -> list[str]:
    """Patch phase: generated matches expected (issue fixed)."""
    failures = []

    if not GENERATED_PATH.exists():
        failures.append("PATCH-01 generated_manifest.yaml must exist during patch phase")
        return failures

    try:
        generated = load_mapping(GENERATED_PATH)
        expected = load_mapping(EXPECTED_PATH)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        failures.append(f"PATCH-02 Fixture YAML invalid: {exc}")
        return failures

    if generated != expected:
        failures.append("PATCH-03 generated Fixture must match expected after patch (issue fixed)")

    if generated.get("synthetic_workflow_version") != "v0.1.0":
        failures.append("PATCH-04 generated Fixture must have synthetic_workflow_version: v0.1.0")

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase-PATCH-FLOW-003 Validator")
    parser.add_argument("--phase", choices=["planning", "development", "patch"], required=True, help="Validation phase")
    args = parser.parse_args()

    print(f"=" * 60)
    print(f"Phase-PATCH-FLOW-003 Validator (phase: {args.phase})")
    print(f"=" * 60)

    failures = []

    # Common checks
    failures.extend(check_planning_assets())
    struct_failures, expected, source = check_fixture_structure()
    failures.extend(struct_failures)
    failures.extend(check_safety_fields(expected, source))

    # Phase-specific checks
    if args.phase == "planning":
        # Planning phase: generated_manifest.yaml should not exist
        if GENERATED_PATH.exists():
            failures.append("PLAN-01 generated_manifest.yaml must not exist during planning phase")
    elif args.phase == "development":
        failures.extend(check_development_phase())
    elif args.phase == "patch":
        failures.extend(check_patch_phase())

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1

    checks = 5 + 1 if args.phase == "planning" else 5 + (5 if args.phase == "development" else 4)
    print(f"PASS Phase-PATCH-FLOW-003 Validator ({args.phase} state, {checks}/{checks})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
