"""Tests for DeepSeek-R1 / V3 Mock CLI Adapter and OpenAgentSec CLI."""

import hashlib
import json
from pathlib import Path
import pytest
import yaml

from src.openagentsec import __version__
from src.openagentsec.cli import audit_summary, eval_module, list_modules, main as cli_main
from workflow_orchestrator.adapters import AdapterConfig, DeepSeekCLIAdapter
from workflow_orchestrator.engine import WorkflowError

ROOT = Path(__file__).resolve().parents[1]


def test_deepseek_adapter_initialization():
    """DeepSeekCLIAdapter must correctly initialize from valid AdapterConfig."""
    config_dict = {
        "executable": "python3",
        "args": ["-m", "deepseek_mock"],
        "prompt_input_mode": "attachment_file",
        "prompt_file_arg": "--prompt-file",
        "cwd_arg": "--cwd",
        "timeout_seconds": 60,
    }
    config = AdapterConfig.from_mapping(config_dict)
    adapter = DeepSeekCLIAdapter(config)

    assert adapter.runtime == "deepseek"
    assert adapter.help_args() == ["--help"]


def test_deepseek_adapter_command_building(tmp_path: Path):
    """DeepSeekCLIAdapter must construct argument list in expected order."""
    config_dict = {
        "executable": "python3",
        "args": ["-m", "deepseek_mock"],
        "prompt_input_mode": "attachment_file",
        "prompt_file_arg": "--prompt-file",
        "cwd_arg": "--cwd",
        "timeout_seconds": 60,
    }
    config = AdapterConfig.from_mapping(config_dict)
    adapter = DeepSeekCLIAdapter(config)

    handoff_file = tmp_path / "handoff.md"
    handoff_file.write_text("Test handoff content", encoding="utf-8")

    cmd = adapter.build_command(handoff_file, tmp_path)
    assert "python3" in cmd[0]
    assert "--cwd" in cmd
    assert "--prompt-file" in cmd
    assert str(handoff_file) in cmd


def test_deepseek_reasoning_trace_extraction():
    """parse_reasoning_and_content must isolate <think> tags from final response."""
    raw = (
        "<think>\n"
        "Step 1: Check security boundaries.\n"
        "Step 2: Ensure no unauthorized tools are invoked.\n"
        "</think>\n"
        "Here is the safe sanitized response for the user query."
    )
    result = DeepSeekCLIAdapter.parse_reasoning_and_content(raw)

    assert result["has_cot"] is True
    assert result["unclosed_think_tag"] is False
    assert len(result["reasoning_trace"]) == 1
    assert "Step 1: Check security boundaries." in result["reasoning_trace"][0]
    assert result["clean_output"] == "Here is the safe sanitized response for the user query."


def test_deepseek_multiple_think_tags_and_unclosed():
    """Adapter must handle multiple think tags and detect unclosed tags."""
    raw = "<think>First thought</think> Middle text <think>Second thought</think> Final answer"
    result = DeepSeekCLIAdapter.parse_reasoning_and_content(raw)

    assert len(result["reasoning_trace"]) == 2
    assert result["clean_output"] == "Middle text  Final answer"

    unclosed_raw = "<think>Incomplete reasoning without closing tag"
    unclosed_res = DeepSeekCLIAdapter.parse_reasoning_and_content(unclosed_raw)
    assert unclosed_res["unclosed_think_tag"] is True


def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_cli_env(tmp_path: Path, module_ids=("M01", "M02")):
    """Scratch repo: registry with M01/M02; M01 has a fully trusted PASS result."""
    reg_dir = tmp_path / "capability_modules"
    reg_dir.mkdir(parents=True)
    (reg_dir / "module_registry.yaml").write_text(
        yaml.dump(
            {
                "modules": [
                    {"module_id": m, "module_name": m, "priority": "P0", "layer": "test"}
                    for m in module_ids
                ]
            }
        ),
        encoding="utf-8",
    )
    exec_dir = tmp_path / "executions" / "phase01_m01"
    exec_dir.mkdir(parents=True)
    (exec_dir / "ev-001").write_text("evidence payload", encoding="utf-8")
    trace_path = exec_dir / "trace.json"
    trace_path.write_text('{"trace": []}', encoding="utf-8")
    body = {
        "module_id": "M01",
        "run_id": "run-001",
        "assessment_mode": "adversarial_validation",
        "maturity_level": "L3",
        "code_version": "6.0.0",
        "evaluator_version": "1.0",
        "evidence_refs": ["ev-001"],
        "artifact_hashes": {
            "trace.json": _hash_file(trace_path),
            "ev-001": _hash_file(exec_dir / "ev-001"),
        },
        "final_status": "PASS",
        "synthetic_only": True,
    }
    result_path = exec_dir / "result.yaml"
    result_path.write_text(yaml.dump(body), encoding="utf-8")
    return tmp_path


def test_openagentsec_cli_functions(tmp_path):
    """OpenAgentSec CLI returns precise statuses and exit codes from trusted results."""
    import src.openagentsec.cli as cli_mod

    root = _make_cli_env(tmp_path)
    old = cli_mod.ROOT
    cli_mod.ROOT = root
    try:
        mods = list_modules()
        assert len(mods) == 2

        # trusted PASS -> exit 0
        assert cli_main(["eval", "-t", "M01"]) == 0

        # registered but no execution results -> NOT_FOUND / 1
        assert cli_main(["eval", "-t", "M02"]) == 1

        # unregistered -> NOT_FOUND / 1
        assert cli_main(["eval", "-t", "M999"]) == 1

        # audit is derived from trusted results, not registry coverage
        audit = audit_summary("json")
        data = json.loads(audit)
        assert data["verdict"] == "implementation_in_progress"
        assert data["pass_count"] == 1
        assert data["not_found_count"] == 1
        assert data["overall_status"] == "INCONCLUSIVE"
        assert cli_main(["audit", "--report", "json"]) == 4
    finally:
        cli_mod.ROOT = old


def test_real_m48_eval_is_not_pass():
    """Real M48 results are legacy/incomplete/ambiguous — never a trusted PASS."""
    import src.openagentsec.cli as cli_mod

    old = cli_mod.ROOT
    cli_mod.ROOT = ROOT
    try:
        rc = eval_module("M48")
        assert rc != 0, (
            "M48 must not return PASS: its current real results are old, incomplete "
            "or ambiguous (multiple candidate result files without run selection)"
        )
    finally:
        cli_mod.ROOT = old
