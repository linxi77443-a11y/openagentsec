"""Packaging regression tests for OpenAgentSec schema assets (PRD v4.0.2 / Phase 1B-P).

Verifies that:
1. All three canonical schema resources are accessible and valid via get_schema()
2. pyproject.toml correctly configures [tool.setuptools.package-data] for openagentsec
3. Python package discovery in src/ preserves all core packages without narrowing
"""

from __future__ import annotations

from pathlib import Path

import pytest
import setuptools
import tomli

from src.openagentsec.models import get_schema

CANONICAL_SCHEMAS = (
    "security_policy",
    "evaluation_objective",
    "target_profile",
)


def test_schema_resources_accessible_via_model_loader() -> None:
    """Verify all three canonical schemas are discoverable and loadable."""
    for schema_name in CANONICAL_SCHEMAS:
        schema = get_schema(schema_name)
        assert isinstance(schema, dict), f"Schema {schema_name} must be a dict"
        assert "$schema" in schema, f"Schema {schema_name} must declare $schema"
        assert "properties" in schema, f"Schema {schema_name} must declare properties"


def test_package_data_configured_in_pyproject() -> None:
    """Verify pyproject.toml explicitly configures package-data for openagentsec schemas."""
    pyproject_path = Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml must exist"

    data = tomli.loads(pyproject_path.read_text(encoding="utf-8"))
    tool_setuptools = data.get("tool", {}).get("setuptools", {})
    package_data = tool_setuptools.get("package-data", {})

    assert "openagentsec" in package_data, "openagentsec package-data must be configured in pyproject.toml"
    patterns = package_data["openagentsec"]
    assert any("schemas/v4" in pat for pat in patterns), (
        "package-data patterns must include schemas/v4"
    )


def test_package_discovery_preserves_all_core_packages() -> None:
    """Verify setuptools.find_packages('src') discovers all baseline core packages."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    src_dir = repo_root / "src"
    discovered = set(setuptools.find_packages(str(src_dir)))

    expected_packages = {
        "openagentsec",
        "openagentsec.models",
        "gatekeeper",
        "engine",
        "engine.v2",
    }
    missing = expected_packages - discovered
    assert not missing, f"Package discovery must not lose core packages: missing {missing}"
