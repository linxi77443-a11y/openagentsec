import os
import py_compile
import pytest
import yaml

def test_gate_script_exists():
    assert os.path.exists("scripts/validate_full_regression_gate.py")

def test_gate_script_compiles():
    # 纯标准库和subprocess调用的保证
    py_compile.compile("scripts/validate_full_regression_gate.py", doraise=True)

def test_task_brief_template_exists():
    assert os.path.exists("automation/runs/TEMPLATE.task_brief.md")

def test_task_brief_template_mandatory_clauses():
    with open("automation/runs/TEMPLATE.task_brief.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "validate_full_regression_gate.py" in content
    assert "delivery.json" in content
    assert "synthetic_only=true" in content

def test_guardrails_exists():
    assert os.path.exists(".agent/rules/project-guardrails.md")

def test_guardrails_has_regression_gate_section():
    with open(".agent/rules/project-guardrails.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "回归门禁" in content
    assert "validate_full_regression_gate.py" in content

def test_gate_script_contains_pytest():
    with open("scripts/validate_full_regression_gate.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "pytest" in content
    assert "tests/" in content

def test_gate_script_runs_validators():
    with open("scripts/validate_full_regression_gate.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert "scripts/validate_" in content
    assert "third_party" in content
