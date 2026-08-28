"""Comprehensive unit tests for OpenAgentSec Framework Architecture & Invariants."""

import json
from pathlib import Path
import pytest
import yaml

from src.openagentsec import __version__
from src.openagentsec.cli import audit_summary, eval_module, list_modules, main as cli_main

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "capability_modules" / "module_registry.yaml"


@pytest.fixture(scope="module")
def registry_data():
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_framework_version():
    """Framework version must be 6.0.0."""
    assert __version__ == "6.0.0"


def test_registry_file_exists():
    """Module registry must be present and valid YAML."""
    assert REGISTRY_PATH.is_file()


def test_registry_modules_count(registry_data):
    """Module registry must contain at least 45 modules."""
    modules = registry_data.get("modules", [])
    assert len(modules) >= 45


@pytest.mark.parametrize("required_module", ["M01", "M02", "M16", "M24", "M25", "M27", "M48", "M49", "M50"])
def test_core_security_modules_exist(registry_data, required_module):
    """All critical P0/P1 security modules must be registered."""
    modules = {m.get("module_id"): m for m in registry_data.get("modules", [])}
    assert required_module in modules
    mod = modules[required_module]
    assert mod.get("module_name")
    assert mod.get("priority") in ("P0", "P1", "P2")


def test_m48_coverage_status_is_mvp_complete(registry_data):
    """M48 must be marked mvp_complete in Epic 1."""
    modules = {m.get("module_id"): m for m in registry_data.get("modules", [])}
    m48 = modules["M48"]
    assert m48["coverage"]["coverage_status"] == "mvp_complete"
    assert m48["coverage"]["implementation_status"] == "mvp_done"


def test_m24_coverage_status_is_mvp_complete(registry_data):
    """M24 must be marked mvp_complete in Epic 2."""
    modules = {m.get("module_id"): m for m in registry_data.get("modules", [])}
    m24 = modules["M24"]
    assert m24["coverage"]["coverage_status"] == "mvp_complete"
    assert m24["coverage"]["implementation_status"] == "mvp_done"


def test_m25_coverage_status_is_mvp_complete(registry_data):
    """M25 must be marked mvp_complete in Epic 2."""
    modules = {m.get("module_id"): m for m in registry_data.get("modules", [])}
    m25 = modules["M25"]
    assert m25["coverage"]["coverage_status"] == "mvp_complete"
    assert m25["coverage"]["implementation_status"] == "mvp_done"


def test_all_modules_have_safety_invariants(registry_data):
    """All registered modules must enforce safety invariants."""
    for mod in registry_data.get("modules", []):
        if mod.get("not_module_mvp") or mod.get("registry_type") == "visualization_readiness_assessment":
            continue
        m_id = mod.get("module_id")
        assert mod.get("formal_finding_allowed") is False, f"{m_id}: formal_finding_allowed must be False"
        assert mod.get("human_review_required") is True, f"{m_id}: human_review_required must be True"


@pytest.mark.parametrize("layer", ["chatbot", "rag", "agent", "reporting", "supply_chain"])
def test_modules_layer_classification(registry_data, layer):
    """Modules must be properly categorized across architectural layers."""
    modules_in_layer = [m for m in registry_data.get("modules", []) if m.get("layer") == layer]
    assert len(modules_in_layer) >= 1, f"Layer {layer} should contain at least one module"


def test_cli_list_modules_output(capsys):
    """CLI list-modules should print table of modules."""
    mods = list_modules()
    assert len(mods) > 0
    captured = capsys.readouterr()
    assert "Module ID" in captured.out
    assert "M48" in captured.out


@pytest.mark.parametrize("target_id", ["M01", "M02", "M16", "M24", "M25", "M48"])
def test_cli_eval_target_modules(target_id, capsys):
    """CLI eval should return a valid status code for known modules."""
    code = eval_module(target_id)
    assert code in (0, 1, 2, 3, 4, 5), f"invalid exit code: {code}"
    captured = capsys.readouterr()
    combined = captured.out + captured.err
    assert target_id in combined


def test_cli_audit_json_format():
    """CLI audit in JSON format must output valid JSON with implementation_in_progress verdict."""
    output = audit_summary("json")
    data = json.loads(output)
    assert data["framework"] == "OpenAgentSec"
    assert data["version"] == "6.0.0"
    assert data["verdict"] == "implementation_in_progress"


def test_cli_audit_yaml_format():
    """CLI audit in YAML format must output valid YAML."""
    output = audit_summary("yaml")
    data = yaml.safe_load(output)
    assert data["framework"] == "OpenAgentSec"
    assert data["total_modules"] >= 45


def test_cli_main_help_and_subcommands(capsys):
    """CLI main dispatcher must handle help and subcommands gracefully."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["--help"])
    assert exc_info.value.code == 0

    ret_list = cli_main(["list-modules"])
    assert ret_list == 0

    ret_eval = cli_main(["eval", "--target", "M48"])
    assert ret_eval in (0, 1, 2, 3, 4, 5), f"unexpected eval exit: {ret_eval}"


def test_readme_file_integrity():
    """README.md must declare OpenAgentSec and license."""
    readme_path = ROOT / "README.md"
    assert readme_path.is_file()
    content = readme_path.read_text(encoding="utf-8")
    assert "OpenAgentSec" in content
    assert "Project Overview" in content or "English Overview" in content
    assert "Apache" in content


def test_license_and_contributing():
    """LICENSE and CONTRIBUTING.md must exist."""
    assert (ROOT / "LICENSE").is_file()
    assert (ROOT / "CONTRIBUTING.md").is_file()
    assert (ROOT / "docs" / "release_notes_v6_0.md").is_file()


def test_release_notes_v6_verdict():
    """Release notes v6.0 must certify Milestone 6.0."""
    notes_path = ROOT / "docs" / "release_notes_v6_0.md"
    content = notes_path.read_text(encoding="utf-8")
    assert "VERDICT_MILESTONE_6_0_PASSED_CERTIFIED" in content
    assert "6.0.0" in content
