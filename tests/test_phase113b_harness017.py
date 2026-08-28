import os
import yaml
import pytest
import sys
sys.path.insert(0, os.path.abspath('.'))
from src.engine.v2.task_suite import load_task_suite, validate_suite, sample_suite

def test_tasks_exists():
    assert os.path.exists("benchmarks/deepseek_suite/tasks_bilingual.yaml")

def test_tasks_size():
    tasks = load_task_suite()
    assert len(tasks) >= 40

def test_manifest_exists():
    assert os.path.exists("benchmarks/deepseek_suite/suite_manifest.yaml")

def test_manifest_content():
    with open("benchmarks/deepseek_suite/suite_manifest.yaml", "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    assert "total_tasks" in manifest
    assert manifest["total_tasks"] >= 40

def test_task_suite_py_exists():
    assert os.path.exists("src/engine/v2/task_suite.py")

def test_validate_suite_valid():
    tasks = load_task_suite()
    assert validate_suite(tasks) is True

def test_validate_suite_invalid_atlas():
    task = {
        "task_id": "test",
        "language": "zh",
        "atlas_technique_id": "invalid_id",
        "intent": "attack_simulation",
        "synthetic_prompt": "<SIM_TEST>",
        "expected_behavior": "safe_refusal",
        "category": "CoT 异常"
    }
    with pytest.raises(ValueError):
        validate_suite([task])

def test_validate_suite_no_sim_prefix():
    tasks = load_task_suite()
    task = tasks[0].copy()
    task["synthetic_prompt"] = "no_sim_prefix"
    with pytest.raises(ValueError):
        validate_suite([task])

def test_validate_suite_category_count():
    task1 = {
        "task_id": "test1",
        "language": "zh",
        "atlas_technique_id": "atlas.llm_prompt_injection",
        "intent": "attack_simulation",
        "synthetic_prompt": "<SIM_TEST>",
        "expected_behavior": "safe_refusal",
        "category": "CoT 异常"
    }
    task2 = task1.copy()
    task2["language"] = "en"
    # Only 1 category, should fail
    with pytest.raises(ValueError):
        validate_suite([task1, task2])

def test_validate_suite_language_count():
    tasks = load_task_suite()
    for t in tasks:
        t["language"] = "zh"
    # Only 1 language, should fail
    with pytest.raises(ValueError):
        validate_suite(tasks)

def test_sample_suite_size():
    tasks = load_task_suite()
    sampled = sample_suite(tasks, 10)
    assert len(sampled) == 10

def test_sample_suite_stratification():
    tasks = load_task_suite()
    sampled = sample_suite(tasks, 10)
    cats = {t["category"] for t in sampled}
    # With 10 samples and 5 categories evenly distributed, it should hit all 5
    assert len(cats) >= 5

def test_demo_script_exists():
    assert os.path.exists("scripts/run_phase113b_suite_demo.py")

def test_report_exists():
    assert os.path.exists("executions/phase113b_harness017/suite_report.yaml")
