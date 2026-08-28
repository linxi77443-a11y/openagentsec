from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import pytest
import yaml

from scripts.workflow import parser as workflow_parser
from tests.test_workflow_orchestrator import Harness, accept_development, write_yaml
from workflow_orchestrator import WorkflowError
from workflow_orchestrator.agent_executor import AgentExecutor
from workflow_orchestrator.agent_run_store import AgentRunStore


TASK_ID = "TASK-AGENT"


FAKE_CLI = r'''#!/usr/bin/env python3
import os
import shutil
import sys
import time
from pathlib import Path

args = sys.argv[1:]
if "--version" in args:
    print("9.9.9-fake")
    raise SystemExit(0)
if "--help" in args:
    modes = "default yolo" if os.environ.get("FAKE_QODER_YOLO", "1") == "1" else "default auto"
    print(f"fake help permission modes: {modes}")
    raise SystemExit(0)

trace = os.environ.get("FAKE_AGENT_TRACE")
if trace:
    with open(trace, "a", encoding="utf-8") as handle:
        handle.write(" ".join(args) + "\n")
behavior = os.environ.get("FAKE_AGENT_BEHAVIOR", "success")
if behavior == "interactive":
    print("Approve this action? [y/N]", flush=True)
    raise SystemExit(0)
if behavior == "nonzero":
    print("fake failure", file=sys.stderr)
    raise SystemExit(7)
if behavior == "sleep":
    time.sleep(30)
if behavior == "missing":
    raise SystemExit(0)

source = os.environ.get("FAKE_RESULT_SOURCE")
target = os.environ.get("FAKE_RESULT_TARGET")
if source and target:
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
scope_path = os.environ.get("FAKE_SCOPE_PATH")
if scope_path:
    Path(scope_path).write_text("out of scope\n", encoding="utf-8")
if os.environ.get("FAKE_EMIT_SECRET") == "1":
    print("API_KEY=super-secret-value")
    print("Authorization: Bearer abc.def.ghi", file=sys.stderr)
print("fake agent complete")
'''


class AdapterHarness:
    def __init__(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        timeout: int = 5,
        qoder_verified_modes: list[str] | None = None,
    ) -> None:
        self.workflow = Harness(
            tmp_path,
            profiles={TASK_ID: "lightweight_non_execution"},
            batch_id="BATCH-AGENT-001",
        )
        self.workflow.init()
        self.fake = tmp_path / "fake-agent"
        self.fake.write_text(FAKE_CLI, encoding="utf-8")
        self.fake.chmod(0o755)
        self.trace = tmp_path / "agent-trace.log"
        self.config = tmp_path / "agent-config.yaml"
        self.timeout = timeout
        self.monkeypatch = monkeypatch
        self.qoder_verified_modes = qoder_verified_modes
        self._write_config()
        monkeypatch.setenv("FAKE_AGENT_TRACE", str(self.trace))
        monkeypatch.setenv("FAKE_QODER_YOLO", "1")
        monkeypatch.setenv("FAKE_AGENT_BEHAVIOR", "success")
        monkeypatch.delenv("FAKE_SCOPE_PATH", raising=False)
        monkeypatch.delenv("FAKE_RESULT_SOURCE", raising=False)
        monkeypatch.delenv("FAKE_RESULT_TARGET", raising=False)
        monkeypatch.delenv("FAKE_EMIT_SECRET", raising=False)

    def _write_config(self, mimo_args: list[str] | None = None) -> None:
        environment = [
            "HOME", "PATH", "FAKE_AGENT_TRACE", "FAKE_QODER_YOLO", "FAKE_AGENT_BEHAVIOR",
            "FAKE_RESULT_SOURCE", "FAKE_RESULT_TARGET", "FAKE_SCOPE_PATH", "FAKE_EMIT_SECRET",
        ]
        qoder_section: dict = {
            "executable": str(self.fake),
            "args": ["--print"],
            "prompt_input_mode": "attachment_file",
            "prompt_file_arg": "--attachment",
            "cwd_arg": "--cwd",
            "timeout_seconds": self.timeout,
            "permission_args": ["--permission-mode", "yolo"],
            "required_permission_mode": "yolo",
        }
        if self.qoder_verified_modes is not None:
            qoder_section["verified_permission_modes"] = self.qoder_verified_modes
        write_yaml(self.config, {
            "config_version": "v0.2",
            "graceful_termination_seconds": 1,
            "hard_kill_after_grace_period": True,
            "partial_result_auto_ingest": False,
            "environment_allowlist": environment,
            "mimo": {
                "executable": str(self.fake),
                "args": mimo_args or ["run"],
                "prompt_input_mode": "attachment_file",
                "prompt_file_arg": "--file",
                "cwd_arg": "--dir",
                "timeout_seconds": self.timeout,
                "permission_args": [],
                "required_permission_mode": None,
            },
            "qoder": qoder_section,
        })

    @property
    def executor(self) -> AgentExecutor:
        return AgentExecutor(self.workflow.engine, self.config)

    def target(self, filename: str) -> Path:
        return self.workflow.runtime / self.workflow.batch_id / TASK_ID / filename

    def result_source(self, source: Path, filename: str) -> Path:
        target = self.target(filename)
        self.monkeypatch.setenv("FAKE_RESULT_SOURCE", str(source))
        self.monkeypatch.setenv("FAKE_RESULT_TARGET", str(target))
        return target

    def develop_source(self) -> tuple[Path, str]:
        source, commit = self.workflow.develop(TASK_ID)
        self.result_source(source, "development_result.yaml")
        return source, commit

    def run_dir(self, result: dict) -> Path:
        return self.workflow.runtime / self.workflow.batch_id / "agent_runs" / TASK_ID / result["run_id"]


@pytest.fixture
def adapter_harness(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AdapterHarness:
    return AdapterHarness(tmp_path, monkeypatch)


def test_dry_run_never_starts_process_and_requires_explicit_mode(adapter_harness: AdapterHarness):
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    assert plan["selected_agent"] == "mimo_development"
    assert plan["process_started"] is False
    assert plan["automatic_ingest_planned"] is True
    assert not adapter_harness.trace.exists()
    with pytest.raises(WorkflowError) as caught:
        adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID)
    assert caught.value.code == "agent_approval_required"
    with pytest.raises(SystemExit):
        workflow_parser().parse_args(["run-agent", "--batch", "B", "--task", "T"])


def test_mimo_uses_attachment_without_permission_override(adapter_harness: AdapterHarness):
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    assert plan["permission_mode"] == "default"
    assert "--file" in plan["sanitized_args"]
    assert "--permission-mode" not in plan["sanitized_args"]
    assert "--dangerously-skip-permissions" not in plan["sanitized_args"]


def test_full_fake_patch_flow_runs_one_agent_at_a_time(adapter_harness: AdapterHarness):
    workflow = adapter_harness.workflow
    _source, delivery = adapter_harness.develop_source()
    development = adapter_harness.executor.run_agent(workflow.batch_id, TASK_ID, approved=True)
    assert development["error"] is None
    assert development["automatic_ingest_performed"] is True
    assert development["final_workflow_state"] == "review_pending"
    assert len(adapter_harness.trace.read_text().splitlines()) == 1

    review_source = workflow.review(TASK_ID, delivery, "patch_required")
    adapter_harness.result_source(review_source, "review_result.yaml")
    review_plan = adapter_harness.executor.dry_run(workflow.batch_id, TASK_ID)
    assert review_plan["selected_agent"] == "qoder_review"
    permission_index = review_plan["sanitized_args"].index("--permission-mode")
    assert review_plan["sanitized_args"][permission_index + 1] == "yolo"
    review = adapter_harness.executor.run_agent(workflow.batch_id, TASK_ID, approved=True)
    assert review["final_workflow_state"] == "patch_pending"

    patch_source, patch_commit = workflow.patch(TASK_ID, delivery)
    adapter_harness.result_source(patch_source, "patch_result.yaml")
    patch = adapter_harness.executor.run_agent(workflow.batch_id, TASK_ID, approved=True)
    assert patch["agent"] == "mimo_patch"
    assert patch["final_workflow_state"] == "patch_review_pending"

    patch_review_source = workflow.review(TASK_ID, patch_commit, "passed", patch_review=True)
    adapter_harness.result_source(patch_review_source, "review_result.yaml")
    patch_review = adapter_harness.executor.run_agent(workflow.batch_id, TASK_ID, approved=True)
    assert patch_review["agent"] == "qoder_patch_review"
    assert patch_review["final_workflow_state"] == "accepted"
    assert len(adapter_harness.trace.read_text().splitlines()) == 4


@pytest.mark.parametrize(
    ("behavior", "expected_error"),
    [("nonzero", "agent_exit_nonzero"), ("missing", "agent_result_missing")],
)
def test_process_and_missing_result_failures_stop_for_human(
    adapter_harness: AdapterHarness,
    behavior: str,
    expected_error: str,
):
    adapter_harness.monkeypatch.setenv("FAKE_AGENT_BEHAVIOR", behavior)
    if behavior == "nonzero":
        adapter_harness.develop_source()
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == expected_error
    assert result["automatic_ingest_performed"] is False
    assert result["final_workflow_state"] == "human_intervention_required"


def test_timeout_stops_without_partial_ingest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    harness = AdapterHarness(tmp_path, monkeypatch, timeout=1)
    harness.monkeypatch.setenv("FAKE_AGENT_BEHAVIOR", "sleep")
    harness.develop_source()
    result = harness.executor.run_agent(harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "agent_timeout"
    assert result["timeout"] is True
    assert result["automatic_ingest_performed"] is False


def test_cancel_terminates_active_agent_and_preserves_logs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    harness = AdapterHarness(tmp_path, monkeypatch, timeout=20)
    harness.monkeypatch.setenv("FAKE_AGENT_BEHAVIOR", "sleep")
    harness.develop_source()
    holder: dict[str, dict] = {}

    def run() -> None:
        holder["result"] = harness.executor.run_agent(harness.workflow.batch_id, TASK_ID, approved=True)

    thread = threading.Thread(target=run)
    thread.start()
    active = None
    deadline = time.time() + 5
    while time.time() < deadline:
        active = AgentRunStore.active(harness.workflow.runtime, harness.workflow.batch_id, TASK_ID)
        if active and active.get("child_pid"):
            break
        time.sleep(0.05)
    assert active and active.get("child_pid")
    cancelled = harness.executor.cancel_agent(harness.workflow.batch_id, TASK_ID)
    thread.join(timeout=10)
    assert cancelled["cancel_requested"] is True
    assert holder["result"]["error"] == "agent_cancelled"
    assert holder["result"]["cancelled"] is True
    assert holder["result"]["automatic_ingest_performed"] is False
    assert (harness.run_dir(holder["result"]) / "stdout.log").exists()


def test_invalid_schema_and_identity_are_not_repaired(adapter_harness: AdapterHarness):
    source, _commit = adapter_harness.workflow.develop(TASK_ID)
    value = yaml.safe_load(source.read_text())
    value["unexpected_field"] = True
    write_yaml(source, value)
    adapter_harness.result_source(source, "development_result.yaml")
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "schema_validation_failed"
    assert result["result_schema_valid"] is False
    assert result["automatic_ingest_performed"] is False


@pytest.mark.parametrize(("field", "value", "expected"), [
    ("batch_id", "WRONG-BATCH", "batch_id_mismatch"),
    ("task_id", "WRONG-TASK", "task_id_mismatch"),
])
def test_result_identity_mismatch_is_rejected(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: str,
    expected: str,
):
    harness = AdapterHarness(tmp_path, monkeypatch)
    source, _commit = harness.workflow.develop(TASK_ID)
    payload = yaml.safe_load(source.read_text())
    payload[field] = value
    write_yaml(source, payload)
    harness.result_source(source, "development_result.yaml")
    result = harness.executor.run_agent(harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == expected
    assert result["automatic_ingest_performed"] is False


def test_review_commit_mismatch_is_rejected(adapter_harness: AdapterHarness):
    delivery = accept_development(adapter_harness.workflow, TASK_ID)
    review = adapter_harness.workflow.review(TASK_ID, delivery)
    payload = yaml.safe_load(review.read_text())
    payload["reviewed_commit"] = adapter_harness.workflow.planning_commit
    payload["delivery_commit"] = adapter_harness.workflow.planning_commit
    write_yaml(review, payload)
    adapter_harness.result_source(review, "review_result.yaml")
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "review_commit_mismatch"
    assert result["automatic_ingest_performed"] is False


def test_agent_scope_violation_is_not_reverted(adapter_harness: AdapterHarness):
    adapter_harness.develop_source()
    forbidden = adapter_harness.workflow.root / "forbidden.txt"
    adapter_harness.monkeypatch.setenv("FAKE_SCOPE_PATH", str(forbidden))
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "agent_scope_violation"
    assert result["automatic_ingest_performed"] is False
    assert "forbidden.txt" in result["modified_files"]
    assert result["head_after"] is not None
    assert forbidden.exists()


def test_qoder_scope_violation_cannot_modify_delivery_assets(adapter_harness: AdapterHarness):
    delivery = accept_development(adapter_harness.workflow, TASK_ID)
    review = adapter_harness.workflow.review(TASK_ID, delivery)
    adapter_harness.result_source(review, "review_result.yaml")
    delivery_asset = adapter_harness.workflow.root / f"outputs/{TASK_ID}.txt"
    adapter_harness.monkeypatch.setenv("FAKE_SCOPE_PATH", str(delivery_asset))
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["agent"] == "qoder_review"
    assert result["error"] == "agent_scope_violation"
    assert result["automatic_ingest_performed"] is False


def test_preexisting_untracked_file_is_preserved_and_not_attributed(adapter_harness: AdapterHarness):
    preexisting = adapter_harness.workflow.root / "preexisting-user-note.txt"
    preexisting.write_text("keep me\n", encoding="utf-8")
    adapter_harness.develop_source()
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] is None
    assert preexisting.read_text(encoding="utf-8") == "keep me\n"
    assert "preexisting-user-note.txt" not in result["modified_files"]


def test_duplicate_start_is_blocked_by_task_lock(adapter_harness: AdapterHarness):
    adapter_harness.develop_source()
    lock = AgentRunStore(adapter_harness.workflow.runtime, adapter_harness.workflow.batch_id, TASK_ID)
    lock.acquire()
    try:
        with pytest.raises(WorkflowError) as caught:
            adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
        assert caught.value.code == "agent_run_already_active"
    finally:
        lock.release()


def test_interactive_approval_detection_stops_without_fallback(adapter_harness: AdapterHarness):
    adapter_harness.monkeypatch.setenv("FAKE_AGENT_BEHAVIOR", "interactive")
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "interactive_approval_detected"
    assert result["interactive_approval_detected"] is True
    assert result["automatic_ingest_performed"] is False


def test_qoder_yolo_unavailable_stops_before_agent_process(adapter_harness: AdapterHarness):
    accept_development(adapter_harness.workflow, TASK_ID)
    adapter_harness.monkeypatch.setenv("FAKE_QODER_YOLO", "0")
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "qoder_yolo_permission_unavailable"
    assert result["automatic_ingest_performed"] is False
    assert not adapter_harness.trace.exists()
    run_dir = adapter_harness.run_dir(result)
    assert {"invocation.yaml", "stdout.log", "stderr.log", "process.json", "result.yaml"}.issubset(
        {path.name for path in run_dir.iterdir()}
    )


def test_approval_is_invalidated_when_handoff_changes(adapter_harness: AdapterHarness, monkeypatch: pytest.MonkeyPatch):
    adapter_harness.develop_source()
    original = adapter_harness.workflow.engine.prepare_agent_execution
    changed = False

    def mutate_once(batch_id: str):
        nonlocal changed
        state = original(batch_id)
        if not changed:
            task = state["tasks"][TASK_ID]
            handoff = Path(task["handoffs"][task["current_state"]])
            handoff.write_text(handoff.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
            changed = True
        return state

    monkeypatch.setattr(adapter_harness.workflow.engine, "prepare_agent_execution", mutate_once)
    result = adapter_harness.executor.run_agent(adapter_harness.workflow.batch_id, TASK_ID, approved=True)
    assert result["error"] == "agent_approval_invalidated"
    assert result["automatic_ingest_performed"] is False
    assert not adapter_harness.trace.exists()


def test_stdout_stderr_and_args_are_sanitized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    harness = AdapterHarness(tmp_path, monkeypatch)
    harness._write_config(["run", "--api-key", "top-secret-arg"])
    harness.monkeypatch.setenv("FAKE_EMIT_SECRET", "1")
    harness.develop_source()
    plan = harness.executor.dry_run(harness.workflow.batch_id, TASK_ID)
    assert "top-secret-arg" not in plan["sanitized_args"]
    result = harness.executor.run_agent(harness.workflow.batch_id, TASK_ID, approved=True)
    run_dir = harness.run_dir(result)
    combined = (run_dir / "stdout.log").read_text() + (run_dir / "stderr.log").read_text()
    assert "super-secret-value" not in combined
    assert "abc.def.ghi" not in combined
    invocation = yaml.safe_load((run_dir / "invocation.yaml").read_text())
    assert "top-secret-arg" not in json.dumps(invocation)


def test_agent_status_reports_fake_versions(adapter_harness: AdapterHarness):
    status = adapter_harness.executor.agent_status()
    assert status["orchestrator_version"] == "v0.2"
    assert status["agents"]["mimo"]["version"] == "9.9.9-fake"
    assert status["agents"]["qoder"]["permission_mode_supported"] is True


# ---------------------------------------------------------------------------
# Qoder YOLO verified_permission_modes override tests
# ---------------------------------------------------------------------------


def test_qoder_yolo_verified_config_overrides_missing_help_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """help 不包含 yolo，但 verified_permission_modes 包含 yolo 时：
    available=True, permission_mode_supported=True, source=user_verified_config。
    """
    harness = AdapterHarness(tmp_path, monkeypatch, qoder_verified_modes=["yolo"])
    harness.monkeypatch.setenv("FAKE_QODER_YOLO", "0")  # help text omits yolo
    status = harness.executor.agent_status()
    qoder = status["agents"]["qoder"]
    assert qoder["available"] is True
    assert qoder["permission_mode_supported"] is True
    assert qoder["permission_mode_verification_source"] == "user_verified_config"
    assert qoder["error"] is None


def test_qoder_yolo_unavailable_without_verified_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """help 不包含 yolo，且没有 verified 配置时：
    available=False, permission_mode_supported=False, error=required_permission_mode_unavailable。
    """
    harness = AdapterHarness(tmp_path, monkeypatch)  # no verified_permission_modes
    harness.monkeypatch.setenv("FAKE_QODER_YOLO", "0")  # help text omits yolo
    status = harness.executor.agent_status()
    qoder = status["agents"]["qoder"]
    assert qoder["available"] is False
    assert qoder["permission_mode_supported"] is False
    assert qoder["permission_mode_verification_source"] is None
    assert qoder["error"] == "required_permission_mode_unavailable"


def test_qoder_command_always_includes_yolo_permission_mode(adapter_harness: AdapterHarness):
    """Qoder 最终真实命令参数始终包含 --permission-mode yolo。"""
    accept_development(adapter_harness.workflow, TASK_ID)
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    assert plan["selected_agent"] == "qoder_review"
    args = plan["sanitized_args"]
    idx = args.index("--permission-mode")
    assert args[idx + 1] == "yolo"


def test_qoder_runtime_rejection_stops_safely_without_fallback(adapter_harness: AdapterHarness):
    """运行时 CLI 拒绝 yolo（非零退出）时：安全停止、不自动 ingest、不回退其他模式。"""
    accept_development(adapter_harness.workflow, TASK_ID)
    adapter_harness.monkeypatch.setenv("FAKE_AGENT_BEHAVIOR", "nonzero")
    result = adapter_harness.executor.run_agent(
        adapter_harness.workflow.batch_id, TASK_ID, approved=True
    )
    assert result["error"] == "agent_exit_nonzero"
    assert result["automatic_ingest_performed"] is False
    assert result["final_workflow_state"] == "human_intervention_required"
    # 命令中仍然包含 --permission-mode yolo，未回退到其他模式
    args = result["sanitized_args"]
    idx = args.index("--permission-mode")
    assert args[idx + 1] == "yolo"


def test_mimo_adapter_unaffected_by_verified_permission_modes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Mimo Adapter 不受 verified_permission_modes 影响。"""
    harness = AdapterHarness(tmp_path, monkeypatch, qoder_verified_modes=["yolo"])
    harness.monkeypatch.setenv("FAKE_QODER_YOLO", "0")  # help text omits yolo
    status = harness.executor.agent_status()
    mimo = status["agents"]["mimo"]
    assert mimo["available"] is True
    assert mimo["permission_mode_supported"] is True
    assert mimo["permission_mode"] is None
    assert mimo["permission_mode_verification_source"] is None
    assert mimo["error"] is None


# ---------------------------------------------------------------------------
# Mimo argument order tests (positional message before --file array)
# ---------------------------------------------------------------------------


def test_mimo_positional_message_precedes_file_arg(adapter_harness: AdapterHarness):
    """short_instruction 位于 --file 之前，不被 array 参数吞并。"""
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    args = plan["sanitized_args"]
    file_idx = args.index("--file")
    # The positional message (prompt_message) must appear before --file
    # Find the prompt message in args (it's the long instruction string)
    prompt_msg = "Execute the attached frozen workflow handoff exactly."
    msg_indices = [i for i, a in enumerate(args) if prompt_msg in a]
    assert msg_indices, "prompt_message not found in sanitized_args"
    assert all(i < file_idx for i in msg_indices), (
        f"prompt_message at {msg_indices} must precede --file at {file_idx}"
    )


def test_mimo_no_positional_args_after_file(adapter_harness: AdapterHarness):
    """--file <handoff> 之后不再出现位置参数。"""
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    args = plan["sanitized_args"]
    file_idx = args.index("--file")
    # After --file there should be exactly one element: the handoff path
    after_file = args[file_idx + 1:]
    assert len(after_file) == 1, f"Expected only handoff path after --file, got: {after_file}"
    # The handoff path should end with .md
    assert after_file[0].endswith(".md")


def test_mimo_argument_structure_matches_expected_order(adapter_harness: AdapterHarness):
    """参数数组语义: [run, <message>, --dir, <root>, --file, <handoff>]。"""
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    args = plan["sanitized_args"]
    # args[0] == "run"
    assert args[0] == "run"
    # args[1] is the positional message (not a flag)
    assert not args[1].startswith("--")
    # args[2] == "--dir"
    assert args[2] == "--dir"
    # args[3] is the working directory (absolute path)
    assert args[3].startswith("/")
    # args[4] == "--file"
    assert args[4] == "--file"
    # args[5] is the handoff path
    assert args[5].endswith(".md")
    # Total length is exactly 6
    assert len(args) == 6


def test_mimo_handoff_and_working_directory_correct(adapter_harness: AdapterHarness):
    """handoff 路径和 working directory 仍正确。"""
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    args = plan["sanitized_args"]
    # working directory is the project root
    dir_idx = args.index("--dir")
    assert args[dir_idx + 1] == str(adapter_harness.workflow.root)
    # handoff path exists and is within runtime
    file_idx = args.index("--file")
    handoff = Path(args[file_idx + 1])
    assert handoff.is_file()
    assert str(handoff).startswith(str(adapter_harness.workflow.runtime))


def test_qoder_args_unaffected_by_mimo_fix(adapter_harness: AdapterHarness):
    """Qoder 参数不受 Mimo 修复影响。"""
    accept_development(adapter_harness.workflow, TASK_ID)
    plan = adapter_harness.executor.dry_run(adapter_harness.workflow.batch_id, TASK_ID)
    assert plan["selected_agent"] == "qoder_review"
    args = plan["sanitized_args"]
    # Qoder still uses --permission-mode yolo --print --cwd <root> --attachment <handoff> <msg>
    perm_idx = args.index("--permission-mode")
    assert args[perm_idx + 1] == "yolo"
    assert "--print" in args
    assert "--cwd" in args
    assert "--attachment" in args
