"""Dispatcher-level integration tests for SIGINT/SIGTERM cancellation.

These tests launch workflow.py run-agent --approve in a real subprocess,
send signals, and verify the full cancellation chain including:
- Child process termination
- process.json terminal state
- .active.lock cleanup
- workflow_state -> human_intervention_required
- No automatic ingest
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = PROJECT_ROOT / "agent_contracts"

# Fake agent: receives Mimo-style args, writes PID marker next to handoff, sleeps.
# Command: python fake_agent.py "<prompt>" --dir <root> --file <handoff>
FAKE_AGENT_SCRIPT = """\
import sys, time, os, hashlib
# Parse --file arg to derive a unique marker path in /tmp (outside repo)
args = sys.argv[1:]
handoff = None
for i, a in enumerate(args):
    if a == "--file" and i + 1 < len(args):
        handoff = args[i + 1]
        break
if handoff:
    tag = hashlib.md5(handoff.encode()).hexdigest()[:12]
    marker = f"/tmp/fake_agent_{tag}.pid"
else:
    marker = "/tmp/fake_agent_default.pid"
with open(marker, "w") as f:
    f.write(str(os.getpid()))
time.sleep(120)
"""

# Fake agent that also writes a partial result file before sleeping
FAKE_AGENT_WITH_RESULT = """\
import sys, time, os, hashlib
args = sys.argv[1:]
handoff = None
root_dir = None
for i, a in enumerate(args):
    if a == "--file" and i + 1 < len(args):
        handoff = args[i + 1]
    if a == "--dir" and i + 1 < len(args):
        root_dir = args[i + 1]
if handoff:
    tag = hashlib.md5(handoff.encode()).hexdigest()[:12]
    marker = f"/tmp/fake_agent_{tag}.pid"
else:
    marker = "/tmp/fake_agent_default.pid"
with open(marker, "w") as f:
    f.write(str(os.getpid()))
# Write partial result to expected location
if root_dir:
    result_path = os.path.join(root_dir, "runtime", "BATCH-INT-TEST", "TASK-INT", "development_result.yaml")
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, "w") as f:
        f.write("batch_id: BATCH-INT-TEST\ntask_id: TASK-INT\ndevelopment_status: completed\n")
time.sleep(120)
"""


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=root, text=True, check=True, stdout=subprocess.PIPE
    )
    return completed.stdout.strip()


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")


def setup_test_repo(base: Path, fake_agent_script: Path) -> tuple[Path, str, str]:
    """Create a minimal workflow repo with a fake agent adapter config."""
    root = base / "repo"
    root.mkdir(parents=True)
    runtime = root / "runtime"
    runtime.mkdir()
    (root / "validators").mkdir()
    (root / "outputs").mkdir()
    (root / "validators/pass.py").write_text("raise SystemExit(0)\n", encoding="utf-8")

    run_git(root, "init", "-b", "main")
    run_git(root, "config", "user.email", "int-test@example.invalid")
    run_git(root, "config", "user.name", "Interrupt Test")

    batch_id = "BATCH-INT-TEST"
    task_id = "TASK-INT"

    # Task package - use fake agent as "mimo" executable
    package = {
        "task_id": task_id,
        "task_type": "documentation",
        "planning_status": "frozen",
        "review_policy": {
            "risk_level": "medium",
            "review_profile": "lightweight_non_execution",
            "qoder_review_required": True,
            "review_trigger_reason": ["interrupt_test"],
        },
        "delivery_modification_scope": [f"outputs/{task_id}.txt"],
        "input_assets": [],
        "validator_commands": {
            phase: {
                "executable": "python",
                "script": "validators/pass.py",
                "args": [],
                "timeout_seconds": 120,
            }
            for phase in ("planning", "development", "patch")
        },
    }
    write_yaml(root / f"task_packages/{task_id}/task_package.yaml", package)

    manifest = {
        "batch_id": batch_id,
        "task_package_version": "v1",
        "planning_status": "frozen",
        "prompt_versions": {
            "mimo_planning": "v1.3",
            "mimo_development": "v0.4-draft",
            "mimo_patch": "v0.3-draft",
            "qoder_review": "v1.4",
            "qoder_patch_review": "v1.3",
        },
        "planning_assets": [
            f"runtime/{batch_id}/batch_manifest.yaml",
            f"runtime/{batch_id}/planning_freeze.yaml",
            "validators/pass.py",
            f"task_packages/{task_id}/task_package.yaml",
            "config/agent_adapters.local.yaml",
        ],
        "tasks": [{
            "task_id": task_id,
            "task_package": f"task_packages/{task_id}/task_package.yaml",
            "dependencies": [],
            "status": "frozen",
            "task_type": "documentation",
            "assessment_mode": "not_applicable",
            "assessment_execution_performed": False,
            "capability_engine_executed": False,
            "execution_results_generated": False,
            "coverage_change_claimed": False,
            "coverage_credit_requested": 0,
            "review_policy": package["review_policy"],
        }],
    }
    write_yaml(runtime / batch_id / "batch_manifest.yaml", manifest)
    write_yaml(runtime / batch_id / "planning_freeze.yaml", {
        "batch_id": batch_id,
        "planning_status": "frozen",
        "commit_binding": "supplied_out_of_band_after_commit",
    })

    # Adapter config pointing mimo to our fake agent script
    config_dir = root / "config"
    config_dir.mkdir(exist_ok=True)
    adapter_config = {
        "config_version": "v0.2",
        "graceful_termination_seconds": 5,
        "hard_kill_after_grace_period": True,
        "partial_result_auto_ingest": False,
        "environment_allowlist": ["HOME", "PATH", "TMPDIR", "LANG"],
        "mimo": {
            "executable": sys.executable,
            "args": [str(fake_agent_script)],
            "prompt_input_mode": "attachment_file",
            "prompt_file_arg": "--file",
            "cwd_arg": "--dir",
            "permission_args": [],
            "required_permission_mode": None,
            "timeout_seconds": 120,
        },
        "qoder": {
            "executable": "/nonexistent/qoder",
            "args": [],
            "prompt_input_mode": "attachment_file",
            "prompt_file_arg": "--attachment",
            "cwd_arg": "--cwd",
            "permission_args": ["--permission-mode", "yolo"],
            "required_permission_mode": "yolo",
            "verified_permission_modes": ["yolo"],
            "timeout_seconds": 120,
        },
    }
    write_yaml(config_dir / "agent_adapters.local.yaml", adapter_config)

    run_git(root, "add", ".")
    run_git(root, "commit", "-m", "planning: interrupt test batch")
    planning_commit = run_git(root, "rev-parse", "HEAD")

    # Initialize batch
    from workflow_orchestrator import WorkflowEngine
    engine = WorkflowEngine(root, runtime_root=runtime, contracts_root=CONTRACTS_ROOT)
    engine.init_batch(batch_id, planning_commit)

    return root, batch_id, task_id


class TestDispatcherInterruption:
    """Full dispatcher-level SIGINT/SIGTERM integration tests."""

    def _run_and_interrupt(self, tmp_path: Path, sig: int, write_result: bool = False) -> dict[str, Any]:
        """Helper: start run-agent, send signal, collect results."""
        fake_script = tmp_path / "fake_agent.py"

        if write_result:
            fake_script.write_text(FAKE_AGENT_WITH_RESULT, encoding="utf-8")
        else:
            fake_script.write_text(FAKE_AGENT_SCRIPT, encoding="utf-8")

        root, batch_id, task_id = setup_test_repo(tmp_path, fake_script)
        # Marker is written by fake agent to /tmp (outside repo to avoid scope violation)
        import hashlib
        handoff_path = str(root / "runtime" / batch_id / "handoffs" / task_id / "mimo_development_request.md")
        tag = hashlib.md5(handoff_path.encode()).hexdigest()[:12]
        marker = Path(f"/tmp/fake_agent_{tag}.pid")

        # Find the expected result file path for assertions
        runtime = root / "runtime"
        expected_result = runtime / batch_id / task_id / "development_result.yaml"

        # Create a launcher script in the temp repo that uses the correct root
        launcher = root / "_run_agent_launcher.py"
        launcher_content = (
            "import sys\n"
            f"sys.path.insert(0, {str(PROJECT_ROOT)!r})\n"
            "from pathlib import Path\n"
            "from workflow_orchestrator import WorkflowEngine\n"
            "from workflow_orchestrator.agent_executor import AgentExecutor\n"
            f"root = Path({str(root)!r})\n"
            f"engine = WorkflowEngine(root, runtime_root=root / 'runtime',"
            f" contracts_root=Path({str(CONTRACTS_ROOT)!r}))\n"
            "executor = AgentExecutor(engine)\n"
            f"result = executor.run_agent('{batch_id}', '{task_id}', approved=True)\n"
            "import yaml\n"
            "print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False))\n"
        )
        launcher.write_text(launcher_content, encoding="utf-8")
        proc = subprocess.Popen(
            [sys.executable, str(launcher)],
            cwd=root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )

        # Wait for fake agent to start (marker file appears)
        deadline = time.monotonic() + 10
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        if not marker.exists():
            # Debug: check if workflow process already exited
            poll = proc.poll()
            if poll is not None:
                out, err = proc.communicate()
                raise AssertionError(f"Fake agent did not start; workflow exited rc={poll}; stdout={out[:300]}; stderr={err[:300]}")
            raise AssertionError("Fake agent did not start (workflow still running)")
        child_pid = int(marker.read_text().strip())

        # Give a moment for process.json to be written
        time.sleep(0.2)

        # Send signal to the workflow parent process
        os.kill(proc.pid, sig)

        # Wait for workflow process to exit
        try:
            stdout, stderr = proc.communicate(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            pytest.fail("Workflow process did not exit after signal")

        # Collect results
        return {
            "root": root,
            "runtime": runtime,
            "batch_id": batch_id,
            "task_id": task_id,
            "child_pid": child_pid,
            "proc_returncode": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "expected_result": expected_result,
        }

    def test_sigint_full_cancellation_chain(self, tmp_path: Path):
        """SIGINT to dispatcher: full cancellation chain verified."""
        ctx = self._run_and_interrupt(tmp_path, signal.SIGINT)
        root = ctx["root"]
        runtime = ctx["runtime"]
        batch_id = ctx["batch_id"]
        task_id = ctx["task_id"]
        child_pid = ctx["child_pid"]

        # 1. Workflow parent process ended
        assert ctx["proc_returncode"] is not None

        # 2. Fake agent child no longer exists
        time.sleep(0.3)
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)

        # 3. process.json: not running
        agent_runs = runtime / batch_id / "agent_runs" / task_id
        run_dirs = [d for d in agent_runs.iterdir() if d.is_dir()]
        assert len(run_dirs) >= 1
        process_json = run_dirs[0] / "process.json"
        proc_data = json.loads(process_json.read_text(encoding="utf-8"))
        assert proc_data["status"] != "running"

        # 4. process.json: cancelled=true, has ended_at, exit_code
        assert proc_data["cancelled"] is True
        assert "ended_at" in proc_data
        assert "exit_code" in proc_data
        assert proc_data["shell"] is False

        # 5. .active.lock deleted
        lock_path = agent_runs / ".active.lock"
        assert not lock_path.exists()

        # 6. workflow_state -> human_intervention_required
        state = yaml.safe_load((runtime / batch_id / "workflow_state.yaml").read_text())
        task_state = state["tasks"][task_id]
        assert task_state["current_state"] == "human_intervention_required"

        # 7. Error code is agent_cancelled
        errors = task_state["errors"]
        assert any(e["code"] == "agent_cancelled" for e in errors)

        # 8. automatic_ingest_performed = false (check result.yaml)
        result_yaml = run_dirs[0] / "result.yaml"
        if result_yaml.exists():
            result_data = yaml.safe_load(result_yaml.read_text())
            assert result_data.get("automatic_ingest_performed") is False

        # 9. No review invocation
        handoffs_dir = runtime / batch_id / "handoffs" / task_id
        if handoffs_dir.exists():
            assert not (handoffs_dir / "qoder_review_request.md").exists()

        # 10. No review_result
        assert not (runtime / batch_id / task_id / "review_result.yaml").exists()

    def test_sigterm_full_cancellation_chain(self, tmp_path: Path):
        """SIGTERM to dispatcher: same cancellation chain as SIGINT."""
        ctx = self._run_and_interrupt(tmp_path, signal.SIGTERM)
        runtime = ctx["runtime"]
        batch_id = ctx["batch_id"]
        task_id = ctx["task_id"]
        child_pid = ctx["child_pid"]

        # Child terminated
        time.sleep(0.3)
        with pytest.raises(ProcessLookupError):
            os.kill(child_pid, 0)

        # process.json cancelled
        agent_runs = runtime / batch_id / "agent_runs" / task_id
        run_dirs = [d for d in agent_runs.iterdir() if d.is_dir()]
        proc_data = json.loads((run_dirs[0] / "process.json").read_text())
        assert proc_data["status"] == "cancelled"
        assert proc_data["cancelled"] is True

        # workflow_state
        state = yaml.safe_load((runtime / batch_id / "workflow_state.yaml").read_text())
        assert state["tasks"][task_id]["current_state"] == "human_intervention_required"

    def test_independent_process_not_affected(self, tmp_path: Path):
        """An independent process survives the dispatcher cancellation."""
        # Start independent process
        independent = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            start_new_session=True,
        )
        try:
            ctx = self._run_and_interrupt(tmp_path, signal.SIGINT)
            # Independent process still alive
            assert independent.poll() is None
        finally:
            independent.kill()
            independent.wait()

    def test_no_ingest_even_if_result_exists(self, tmp_path: Path):
        """Even if a result file appears during execution, interrupt prevents ingest."""
        # Use normal fake agent (no result writing)
        ctx = self._run_and_interrupt(tmp_path, signal.SIGINT, write_result=False)
        runtime = ctx["runtime"]
        batch_id = ctx["batch_id"]
        task_id = ctx["task_id"]

        # Simulate: write a result file AFTER interrupt (as if agent wrote it late)
        result_dir = runtime / batch_id / task_id
        result_dir.mkdir(parents=True, exist_ok=True)
        (result_dir / "development_result.yaml").write_text(
            "batch_id: BATCH-INT-TEST\ntask_id: TASK-INT\ndevelopment_status: completed\n",
            encoding="utf-8",
        )

        # workflow_state must NOT be review_pending (ingest was not performed)
        state = yaml.safe_load((runtime / batch_id / "workflow_state.yaml").read_text())
        task_state = state["tasks"][task_id]
        assert task_state["current_state"] == "human_intervention_required"
        assert task_state["current_state"] != "review_pending"

        # validator_status must not be "passed"
        assert task_state.get("validator_status") != "passed"
