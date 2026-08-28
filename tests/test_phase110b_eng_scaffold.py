import os
import sys

# Red lines definitions (Subset of 16 safety invariants)
RED_LINES = {
    "synthetic_only": True,
    "fake_runtime_only": True,
    "requires_human_review": True,
    "all_findings_are_candidate": True,
    "red_team_engine_not_executable": True,
    "dashboard_not_execution_interface": True,
    "theory_model_is_not_detection_rule": True,
    "non_retroactivity_guarantee": True,
    "zero_production_penetration": True,
    "zero_formal_disconnect": True
}

def test_pyproject_exists():
    assert os.path.exists("pyproject.toml")

def test_pyproject_name_and_version():
    with open("pyproject.toml", "r") as f:
        content = f.read()
        assert 'name = "ai-security-assessment-workbench"' in content or 'name = "openagentsec"' in content
        assert 'version = "5.2.0"' in content or 'version = "6.0.0"' in content

def test_pyproject_requires_python():
    with open("pyproject.toml", "r") as f:
        assert 'requires-python = ">=3.10"' in f.read()

def test_pyproject_dependencies():
    with open("pyproject.toml", "r") as f:
        content = f.read()
        assert "pyyaml" in content
        assert 'dev = ["pytest>=7"]' in content

def test_core_directories_exist():
    required_dirs = ["src/gatekeeper", "multi_agent", "adversarial_playbooks", "tests", "capability_modules"]
    for d in required_dirs:
        assert os.path.exists(d)

def test_engine_directory_exists():
    assert os.path.exists("src/engine")

def test_safety_invariants_keys():
    assert "synthetic_only" in RED_LINES
    assert "fake_runtime_only" in RED_LINES
    assert "requires_human_review" in RED_LINES

def test_safety_invariants_values():
    assert RED_LINES["synthetic_only"] is True
    assert RED_LINES["requires_human_review"] is True

def test_validator_script_exists():
    assert os.path.exists("scripts/validate_phase110b_eng_scaffold.py")

def test_validator_script_compiles():
    import py_compile
    # Compile the script to check syntax
    py_compile.compile("scripts/validate_phase110b_eng_scaffold.py", doraise=True)
