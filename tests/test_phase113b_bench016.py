import os
import yaml
import pytest
import sys
sys.path.insert(0, os.path.abspath('.'))
from src.engine.v2.leaderboard import load_benchmark_dataset, validate_leaderboard_entry, render_leaderboard_table

def test_dataset_exists():
    assert os.path.exists("benchmarks/preset_leaderboard/dataset.yaml")

def test_dataset_size():
    data = load_benchmark_dataset()
    assert len(data) >= 51

def test_schema_exists():
    assert os.path.exists("benchmarks/preset_leaderboard/leaderboard_schema.yaml")

def test_schema_content():
    with open("benchmarks/preset_leaderboard/leaderboard_schema.yaml", "r") as f:
        schema = yaml.safe_load(f)
    assert "required" in schema
    assert "synthetic_only" in schema["required"]

def test_leaderboard_py_exists():
    assert os.path.exists("src/engine/v2/leaderboard.py")

def test_sample_entries_exists():
    assert os.path.exists("benchmarks/preset_leaderboard/sample_entries.yaml")

def test_sample_entries_size():
    with open("benchmarks/preset_leaderboard/sample_entries.yaml", "r") as f:
        data = yaml.safe_load(f)
    assert len(data.get("entries", [])) >= 5

def test_validate_entry_valid():
    entry = {
        "model_name": "<SIM_TEST>",
        "model_family": "test",
        "eval_date": "2026-08-19T00:00:00Z",
        "mode": "static",
        "coverage_depth": 1.0,
        "safety_level": "high",
        "f1": 0.9,
        "benign_use_correctness": 0.9,
        "refusal_ratio": 0.1,
        "adaptive_residual_risk": 0.05,
        "synthetic_only": True,
        "requires_human_review": True
    }
    assert validate_leaderboard_entry(entry) is True

def test_validate_entry_missing_keys():
    entry = {
        "model_name": "<SIM_TEST>"
    }
    with pytest.raises(ValueError):
        validate_leaderboard_entry(entry)

def test_validate_entry_not_synthetic_only():
    entry = {
        "model_name": "<SIM_TEST>",
        "model_family": "test",
        "eval_date": "2026-08-19T00:00:00Z",
        "mode": "static",
        "coverage_depth": 1.0,
        "safety_level": "high",
        "f1": 0.9,
        "benign_use_correctness": 0.9,
        "refusal_ratio": 0.1,
        "adaptive_residual_risk": 0.05,
        "synthetic_only": False,
        "requires_human_review": True
    }
    with pytest.raises(ValueError):
        validate_leaderboard_entry(entry)

def test_validate_entry_not_requires_human_review():
    entry = {
        "model_name": "<SIM_TEST>",
        "model_family": "test",
        "eval_date": "2026-08-19T00:00:00Z",
        "mode": "static",
        "coverage_depth": 1.0,
        "safety_level": "high",
        "f1": 0.9,
        "benign_use_correctness": 0.9,
        "refusal_ratio": 0.1,
        "adaptive_residual_risk": 0.05,
        "synthetic_only": True,
        "requires_human_review": False
    }
    with pytest.raises(ValueError):
        validate_leaderboard_entry(entry)

def test_render_leaderboard():
    entry = {
        "model_name": "<SIM_TEST>",
        "model_family": "test",
        "eval_date": "2026-08-19T00:00:00Z",
        "mode": "static",
        "coverage_depth": 1.0,
        "safety_level": "high",
        "f1": 0.9,
        "benign_use_correctness": 0.9,
        "refusal_ratio": 0.1,
        "adaptive_residual_risk": 0.05,
        "synthetic_only": True,
        "requires_human_review": True
    }
    md = render_leaderboard_table([entry])
    assert "synthetic_only=true" in md
    assert "requires_human_review=true" in md

def test_demo_script_exists():
    assert os.path.exists("scripts/run_phase113b_bench_demo.py")

def test_preview_exists():
    assert os.path.exists("executions/phase113b_bench016/leaderboard_preview.md")
