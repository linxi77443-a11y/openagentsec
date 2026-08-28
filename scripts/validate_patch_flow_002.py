#!/usr/bin/env python3
"""Read-only Validator for the Phase-PATCH-FLOW-002 synthetic planning/delivery assets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "workflow_test_fixtures" / "patch_flow_002"
EXPECTED_PATH = FIXTURE_DIR / "expected_manifest.yaml"
SOURCE_PATH = FIXTURE_DIR / "source_manifest.yaml"
GENERATED_PATH = FIXTURE_DIR / "generated_manifest.yaml"
TASK_PACKAGE_PATH = ROOT / "task_packages" / "Phase-PATCH-FLOW-002" / "task_package.yaml"
BATCH_MANIFEST_PATH = ROOT / "runtime" / "BATCH-2026-07-20-006" / "batch_manifest.yaml"
PLANNING_FREEZE_PATH = ROOT / "runtime" / "BATCH-2026-07-20-006" / "planning_freeze.yaml"


def load_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"YAML top level must be a mapping: {path}")
    return value


def main() -> int:
    failures: list[str] = []

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

    try:
        expected = load_mapping(EXPECTED_PATH)
        source = load_mapping(SOURCE_PATH)
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        failures.append(f"PL-02 Fixture YAML invalid: {exc}")
        expected = {}
        source = {}

    if expected.get("synthetic_workflow_version") != "v0.1.0":
        failures.append("PL-03 expected Fixture must define synthetic_workflow_version: v0.1.0")
    if "synthetic_workflow_version" in source:
        failures.append("PL-03 source Fixture must omit synthetic_workflow_version for the intended review issue")

    if GENERATED_PATH.exists():
        try:
            generated = load_mapping(GENERATED_PATH)
            if generated != source:
                failures.append("PL-04 generated Fixture must exactly match the frozen source before patching")
        except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
            failures.append(f"PL-04 generated Fixture YAML invalid: {exc}")

    for label, value in (("expected", expected), ("source", source)):
        if value.get("synthetic_only") is not True:
            failures.append(f"PL-05 {label} Fixture must set synthetic_only: true")
        if value.get("real_data_used") is not False:
            failures.append(f"PL-05 {label} Fixture must set real_data_used: false")
        if value.get("external_targets_allowed") is not False:
            failures.append(f"PL-05 {label} Fixture must set external_targets_allowed: false")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    phase = "planning" if not GENERATED_PATH.exists() else "development"
    print(f"PASS Phase-PATCH-FLOW-002 Validator ({phase} state, 5/5)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
