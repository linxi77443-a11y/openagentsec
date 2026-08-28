from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import jsonschema
import pytest
import yaml

from workflow_orchestrator import WorkflowEngine, WorkflowError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_ROOT = PROJECT_ROOT / "agent_contracts"
BATCH_ID = "BATCH-TEST-001"


def run_git(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, check=True, stdout=subprocess.PIPE)
    return completed.stdout.strip()


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")


def review_policy(profile: str) -> dict[str, Any]:
    return {
        "risk_level": {"validator_only": "low", "lightweight_non_execution": "medium", "full_execution": "high"}[profile],
        "review_profile": profile,
        "qoder_review_required": profile != "validator_only",
        "review_trigger_reason": [f"{profile}_test"],
    }


class Harness:
    def __init__(
        self,
        base: Path,
        fail_validator_task: str | None = None,
        profiles: dict[str, str] | None = None,
        batch_id: str = BATCH_ID,
        phase_aware_validator: bool = False,
        validator_args_by_phase: dict[str, list[str]] | None = None,
    ) -> None:
        self.root = base / "repo"
        self.runtime = self.root / "runtime"
        self.incoming = base / "incoming"
        self.root.mkdir(parents=True)
        self.runtime.mkdir()
        self.incoming.mkdir()
        self.batch_id = batch_id
        run_git(self.root, "init", "-b", "main")
        run_git(self.root, "config", "user.email", "workflow-test@example.invalid")
        run_git(self.root, "config", "user.name", "Workflow Test")
        (self.root / "validators").mkdir()
        (self.root / "outputs").mkdir()
        (self.root / "validators/pass.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        (self.root / "validators/fail.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
        if phase_aware_validator:
            (self.root / "validators/phase.py").write_text(
                "import argparse\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--phase', choices=['planning', 'development', 'patch'], required=True)\n"
                "args = parser.parse_args()\n"
                "print(f'phase={args.phase}')\n",
                encoding="utf-8",
            )
        self.profiles = profiles or {
            "TASK-VALIDATOR": "validator_only",
            "TASK-LIGHT": "lightweight_non_execution",
            "TASK-FULL": "full_execution",
        }
        manifest_tasks = []
        for task_id, profile in self.profiles.items():
            package_path = f"task_packages/{task_id}/task_package.yaml"
            validator_file = (
                "fail.py" if task_id == fail_validator_task
                else "phase.py" if phase_aware_validator
                else "pass.py"
            )
            package = {
                "task_id": task_id,
                "task_type": "module_development" if profile == "full_execution" else "documentation",
                "planning_status": "frozen",
                "review_policy": review_policy(profile),
                "delivery_modification_scope": [f"outputs/{task_id}.txt"],
                "input_assets": [],
                "validator_commands": {
                    phase: {
                        "executable": "python",
                        "script": f"validators/{validator_file}",
                        "args": (
                            validator_args_by_phase.get(phase, [])
                            if validator_args_by_phase is not None
                            else ["--phase", phase] if phase_aware_validator
                            else []
                        ),
                        "timeout_seconds": 120,
                    }
                    for phase in ("planning", "development", "patch")
                },
            }
            write_yaml(self.root / package_path, package)
            manifest_task = {
                "task_id": task_id,
                "task_package": package_path,
                "dependencies": [],
                "status": "frozen",
                "task_type": package["task_type"],
                "assessment_mode": "adversarial_validation" if profile == "full_execution" else "not_applicable",
                "assessment_execution_performed": profile == "full_execution",
                "capability_engine_executed": profile == "full_execution",
                "execution_results_generated": profile == "full_execution",
                "coverage_change_claimed": False,
                "coverage_credit_requested": 0,
                "review_policy": review_policy(profile),
            }
            manifest_tasks.append(manifest_task)
        manifest = {
            "batch_id": self.batch_id,
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
                f"runtime/{self.batch_id}/batch_manifest.yaml",
                f"runtime/{self.batch_id}/planning_freeze.yaml",
                "validators/pass.py",
                "validators/fail.py",
                *(["validators/phase.py"] if phase_aware_validator else []),
                *[item["task_package"] for item in manifest_tasks],
            ],
            "tasks": manifest_tasks,
        }
        write_yaml(self.runtime / self.batch_id / "batch_manifest.yaml", manifest)
        write_yaml(self.runtime / self.batch_id / "planning_freeze.yaml", {
            "batch_id": self.batch_id,
            "planning_status": "frozen",
            "commit_binding": "supplied_out_of_band_after_commit",
        })
        run_git(self.root, "add", ".")
        run_git(self.root, "commit", "-m", "planning: test batch")
        self.planning_commit = run_git(self.root, "rev-parse", "HEAD")
        self.engine = WorkflowEngine(self.root, runtime_root=self.runtime, contracts_root=CONTRACTS_ROOT)

    def init(self) -> dict[str, Any]:
        return self.engine.init_batch(self.batch_id, self.planning_commit)

    def develop(
        self,
        task_id: str,
        unexpected: bool = False,
        include_planning_asset: bool = False,
    ) -> tuple[Path, str]:
        relative = f"unexpected/{task_id}.txt" if unexpected else f"outputs/{task_id}.txt"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"development for {task_id}\n", encoding="utf-8")
        modified_files = [relative]
        if include_planning_asset:
            package_path = f"task_packages/{task_id}/task_package.yaml"
            package = self.root / package_path
            package.write_text(package.read_text(encoding="utf-8") + "\n# forbidden delivery edit\n", encoding="utf-8")
            modified_files.append(package_path)
        run_git(self.root, "add", *modified_files)
        run_git(self.root, "commit", "-m", f"dev: {task_id}")
        commit = run_git(self.root, "rev-parse", "HEAD")
        profile = self.profiles[task_id]
        result = {
            "batch_id": self.batch_id,
            "task_id": task_id,
            "development_status": "completed",
            "planning_commit": self.planning_commit,
            "delivery_commit": commit,
            "modified_files": modified_files,
            "validator_name": self.engine.load_state(self.batch_id)["tasks"][task_id]["validator"]["name"],
            "validator_status": "passed",
            "validator_failed_count": 0,
            "artifacts": [],
            "errors": [],
            "review_policy": review_policy(profile),
            "review_policy_escalation": {"required": False},
        }
        incoming = self.incoming / task_id / "development_result.yaml"
        write_yaml(incoming, result)
        return incoming, commit

    def review(self, task_id: str, commit: str, status: str = "passed", patch_review: bool = False) -> Path:
        issue = {
            "issue_id": "ISSUE-001", "task_id": task_id, "severity": "medium",
            "file": f"outputs/{task_id}.txt", "line_or_section": "1",
            "evidence": "synthetic test evidence", "required_fix": "fix test content",
            "acceptance_check": "validator passes",
        }
        failed_patch_review = patch_review and status == "patch_required"
        result = {
            "batch_id": self.batch_id,
            "task_id": task_id,
            "review_stage": "patch" if patch_review else "initial",
            "review_round": 2 if patch_review else 1,
            "review_profile": self.profiles[task_id],
            "reviewer": {"runtime": "qoder", "model": "deepseek"},
            "review_status": status,
            "validator_verified": True,
            "issues": [] if status == "passed" else [issue],
            "warnings": [],
            "coverage_decision": {"coverage_change_claimed": False, "coverage_credit_granted": 0},
            "registry_state_synchronized": True,
            "safety_verified": True,
            "workflow_error": False,
            "human_intervention_required": failed_patch_review,
            "next_action": "task_accepted" if status == "passed" else ("stop_for_human_intervention" if failed_patch_review else "request_patch"),
        }
        if patch_review:
            result["reviewed_base_commit"] = self.engine.load_state(self.batch_id)["tasks"][task_id]["delivery_commit"]
            result["reviewed_patch_commit"] = commit
        else:
            result["delivery_commit"] = commit
            result["reviewed_commit"] = commit
            result["reviewed_commit_matches_delivery_commit"] = True
        path = self.incoming / task_id / ("patch_review" if patch_review else "review") / "review_result.yaml"
        write_yaml(path, result)
        return path

    def patch(self, task_id: str, base_delivery_commit: str, unexpected: bool = False) -> tuple[Path, str]:
        relative = f"unexpected/{task_id}-patch.txt" if unexpected else f"outputs/{task_id}.txt"
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(existing + "patched\n", encoding="utf-8")
        run_git(self.root, "add", relative)
        run_git(self.root, "commit", "-m", f"patch: {task_id} ISSUE-001")
        patch_commit = run_git(self.root, "rev-parse", "HEAD")
        result = {
            "batch_id": self.batch_id,
            "task_id": task_id,
            "review_profile": self.profiles[task_id],
            "base_delivery_commit": base_delivery_commit,
            "patch_commit": patch_commit,
            "fixed_issue_ids": ["ISSUE-001"],
            "modified_files": [relative],
            "validator_status": "passed",
            "remaining_known_issues": [],
            "errors": [],
        }
        incoming = self.incoming / task_id / "patch_result.yaml"
        write_yaml(incoming, result)
        return incoming, patch_commit


@pytest.fixture
def harness(tmp_path: Path) -> Harness:
    value = Harness(tmp_path)
    value.init()
    return value


def accept_development(harness: Harness, task_id: str) -> str:
    result, commit = harness.develop(task_id)
    harness.engine.ingest(harness.batch_id, task_id, result)
    return commit


def accept_review(harness: Harness, task_id: str) -> str:
    commit = accept_development(harness, task_id)
    harness.engine.ingest(harness.batch_id, task_id, harness.review(task_id, commit))
    return commit


def fail_development_schema_then_correct(
    harness: Harness,
    task_id: str = "TASK-LIGHT",
    unexpected: bool = False,
) -> tuple[Path, str, str]:
    result, commit = harness.develop(task_id, unexpected=unexpected)
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["unexpected_metadata"] = "schema failure for retry test"
    write_yaml(result, value)
    original_digest = hashlib.sha256(result.read_bytes()).hexdigest()
    with pytest.raises(WorkflowError) as caught:
        harness.engine.ingest(harness.batch_id, task_id, result)
    assert caught.value.code == "schema_validation_failed"
    value.pop("unexpected_metadata")
    write_yaml(result, value)
    return result, commit, original_digest


def fail_machine_result_schema_then_correct(
    harness: Harness,
    task_id: str,
    result: Path,
) -> str:
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["unexpected_metadata"] = "schema failure for retry test"
    write_yaml(result, value)
    original_digest = hashlib.sha256(result.read_bytes()).hexdigest()
    with pytest.raises(WorkflowError) as caught:
        harness.engine.ingest(harness.batch_id, task_id, result)
    assert caught.value.code == "schema_validation_failed"
    value.pop("unexpected_metadata")
    write_yaml(result, value)
    return original_digest


def force_legacy_validator_without_args(harness: Harness, task_id: str) -> None:
    state = harness.engine.load_state(harness.batch_id)
    task = state["tasks"][task_id]
    command = task["validator"]["commands"]["development"]
    task["validator"] = {
        "name": Path(command["script"]).name,
        "path": command["script"],
        "command": [sys.executable, command["script"]],
    }
    task["last_validator_execution"] = None
    write_yaml(harness.engine.state_path(harness.batch_id), state)


def seed_legacy_validator_runner_failure(
    harness: Harness,
    task_id: str,
    result: Path,
    delivery_commit: str,
) -> None:
    """Reproduce the persisted V0.1.4 runner defect without using the fixed runner."""
    force_legacy_validator_without_args(harness, task_id)
    state = harness.engine.load_state(harness.batch_id)
    task = state["tasks"][task_id]
    canonical = harness.engine.batch_dir(harness.batch_id) / task_id / "development_result.yaml"
    canonical.parent.mkdir(parents=True, exist_ok=True)
    canonical.write_bytes(result.read_bytes())
    task["delivery_commit"] = delivery_commit
    task["current_task_commit_scope_verified"] = True
    task["validator_status"] = "failed"
    task["final_status"] = "pending"
    task["ingested_results"]["development_result.yaml"] = hashlib.sha256(result.read_bytes()).hexdigest()
    execution = {
        "phase": "development",
        "executable": "python",
        "script": task["validator"]["path"],
        "args": [],
        "resolved_command": list(task["validator"]["command"]),
        "timeout_seconds": 120,
        "source_format": "legacy_state_command_adapter",
        "exit_code": 2,
        "stdout": "",
        "stderr": "error: the following arguments are required: --phase\n",
        "timed_out": False,
    }
    task["last_validator_execution"] = execution
    task["errors"].append({
        "code": "task_validator_failed",
        "message": "Recorded status=passed; actual exit_code=2",
    })
    events: list[dict[str, Any]] = []
    harness.engine._transition(
        state,
        task,
        "validator_failed",
        "task_validator_failed",
        events,
        {
            "recorded_status": "passed",
            "recorded_failed_count": 0,
            "actual_exit_code": 2,
            "validator_execution": execution,
        },
    )
    harness.engine._persist(state, events)


def manifest_for_count(task_count: int) -> dict[str, Any]:
    tasks = []
    for index in range(task_count):
        task_id = f"TASK-{index + 1:03d}"
        tasks.append({
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
            "review_policy": review_policy("validator_only"),
        })
    return {
        "batch_id": "BATCH-COUNT-TEST",
        "task_package_version": "v1",
        "planning_status": "frozen",
        "prompt_versions": {
            "mimo_planning": "v1.3",
            "mimo_development": "v0.4-draft",
            "mimo_patch": "v0.3-draft",
            "qoder_review": "v1.4",
            "qoder_patch_review": "v1.3",
        },
        "planning_assets": ["runtime/BATCH-COUNT-TEST/batch_manifest.yaml"],
        "tasks": tasks,
    }


def manifest_validator() -> jsonschema.Draft202012Validator:
    schema = yaml.safe_load((CONTRACTS_ROOT / "batch_manifest.schema.yaml").read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


@pytest.mark.parametrize("task_count", [1, 3, 7, 10])
def test_manifest_accepts_supported_task_counts(task_count: int):
    assert list(manifest_validator().iter_errors(manifest_for_count(task_count))) == []


def test_manifest_rejects_empty_task_list():
    errors = list(manifest_validator().iter_errors(manifest_for_count(0)))
    assert errors
    assert any("non-empty" in error.message for error in errors)


def test_manifest_rejects_eleven_tasks_and_builds_lossless_split_plan():
    manifest = manifest_for_count(11)
    errors = list(manifest_validator().iter_errors(manifest))
    assert errors
    assert any("too long" in error.message for error in errors)

    engine = WorkflowEngine(PROJECT_ROOT)
    plan = engine.build_batch_split_plan(manifest["batch_id"], manifest)
    assert plan["batch_split_required"] is True
    assert [batch["task_count"] for batch in plan["batches"]] == [10, 1]
    assert [
        task_id
        for batch in plan["batches"]
        for task_id in batch["task_ids"]
    ] == [task["task_id"] for task in manifest["tasks"]]
    assert sum(batch["task_count"] for batch in plan["batches"]) == 11
    assert plan["task_order_preserved"] is True
    assert plan["task_ids_preserved"] is True
    assert plan["tasks_truncated"] is False


def test_default_and_user_specified_task_counts_are_preserved():
    engine = WorkflowEngine(PROJECT_ROOT)
    assert engine.requested_task_count(None) == 7
    assert engine.requested_task_count(1) == 1
    assert engine.requested_task_count(10) == 10
    assert engine.requested_task_count(11) == 11


def test_single_task_validator_only_batch_completes(tmp_path: Path):
    single = Harness(tmp_path, profiles={"TASK-ONLY": "validator_only"})
    single.init()
    accept_development(single, "TASK-ONLY")
    summary = single.engine.write_summary(BATCH_ID)
    assert summary["task_count"] == 1
    assert summary["tasks"]["TASK-ONLY"]["acceptance_mode"] == "validator_only"
    assert summary["all_tasks_accepted"] is True


def test_single_task_qoder_review_batch_completes(tmp_path: Path):
    single = Harness(tmp_path, profiles={"TASK-ONLY": "lightweight_non_execution"})
    single.init()
    accept_review(single, "TASK-ONLY")
    summary = single.engine.write_summary(BATCH_ID)
    assert summary["task_count"] == 1
    assert summary["tasks"]["TASK-ONLY"]["review_status"] == "passed"
    assert summary["tasks"]["TASK-ONLY"]["acceptance_mode"] == "qoder_review"
    assert summary["all_tasks_accepted"] is True


def test_init_with_eleven_tasks_reports_split_required(tmp_path: Path):
    profiles = {f"TASK-{index:03d}": "validator_only" for index in range(1, 12)}
    oversized = Harness(tmp_path, profiles=profiles)
    with pytest.raises(WorkflowError) as caught:
        oversized.init()
    error = caught.value.as_dict()
    assert caught.value.code == "batch_split_required"
    assert error["state"] == "workflow_error"
    assert error["batch_split_required"] is True
    assert [batch["task_count"] for batch in error["batches"]] == [10, 1]
    assert sum(batch["task_count"] for batch in error["batches"]) == 11


def test_new_run_yaml_error_never_uses_historical_adapter(tmp_path: Path):
    runtime = tmp_path / "runtime"
    batch_id = "BATCH-NEW-MALFORMED"
    manifest_path = runtime / batch_id / "batch_manifest.yaml"
    manifest_path.parent.mkdir(parents=True)
    valid_prefix = yaml.safe_dump(
        {**manifest_for_count(1), "batch_id": batch_id},
        allow_unicode=True,
        sort_keys=False,
    )
    manifest_path.write_text(
        valid_prefix
        + "dependency_matrix:\n"
        + "  - task_id: TASK-001\n"
        + "    blocked_by: []\n"
        + "  independence_verified: true\n",
        encoding="utf-8",
    )
    engine = WorkflowEngine(PROJECT_ROOT, runtime_root=runtime, contracts_root=CONTRACTS_ROOT)
    with pytest.raises(WorkflowError) as caught:
        engine.validate_batch(batch_id)
    assert caught.value.code == "yaml_read_failed"
    assert caught.value.as_dict()["state"] == "workflow_error"
    with pytest.raises(WorkflowError) as replay_error:
        engine.replay_batch(batch_id)
    assert replay_error.value.code == "historical_compatibility_not_allowed"


def test_mixed_three_task_batch_initializes_independent_states(harness: Harness):
    state = harness.engine.load_state(BATCH_ID)
    assert len(state["tasks"]) == 3
    assert {item["review_profile"] for item in state["tasks"].values()} == {
        "validator_only", "lightweight_non_execution", "full_execution"
    }
    assert all(item["current_state"] == "development_pending" for item in state["tasks"].values())


def test_validator_only_is_accepted_without_qoder_review(harness: Harness):
    accept_development(harness, "TASK-VALIDATOR")
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    assert task["current_state"] == "accepted"
    assert task["acceptance_mode"] == "validator_only"
    assert task["review_status"] is None


def test_runtime_escalation_routes_validator_only_to_qoder(harness: Harness):
    result, _commit = harness.develop("TASK-VALIDATOR")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["review_policy_escalation"] = {
        "required": True,
        "proposed_profile": "lightweight_non_execution",
        "reason": "shared asset discovered during development",
    }
    write_yaml(result, value)
    harness.engine.ingest(BATCH_ID, "TASK-VALIDATOR", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    assert task["current_state"] == "review_pending"
    assert task["effective_review_profile"] == "lightweight_non_execution"
    assert task["qoder_review_required"] is True


def test_lightweight_review_passed(harness: Harness):
    accept_review(harness, "TASK-LIGHT")
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] == "accepted"
    assert task["acceptance_mode"] == "qoder_review"


def test_full_execution_review_passed(harness: Harness):
    accept_review(harness, "TASK-FULL")
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-FULL"]
    assert task["current_state"] == "accepted"
    assert task["review_status"] == "passed"


def test_one_review_pending_while_other_tasks_are_accepted(harness: Harness):
    accept_development(harness, "TASK-VALIDATOR")
    accept_development(harness, "TASK-LIGHT")
    accept_review(harness, "TASK-FULL")
    summary = harness.engine.write_summary(BATCH_ID)
    assert summary["counts"]["accepted"] == 2
    assert summary["counts"]["review_pending"] == 1
    assert summary["batch_state"] == "partially_accepted"


def test_patch_required_does_not_reopen_accepted_tasks(harness: Harness):
    accept_development(harness, "TASK-VALIDATOR")
    light_commit = accept_development(harness, "TASK-LIGHT")
    accept_review(harness, "TASK-FULL")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", light_commit, "patch_required"))
    state = harness.engine.load_state(BATCH_ID)
    assert state["tasks"]["TASK-LIGHT"]["current_state"] == "patch_pending"
    assert state["tasks"]["TASK-VALIDATOR"]["current_state"] == "accepted"
    assert state["tasks"]["TASK-FULL"]["current_state"] == "accepted"


def test_patch_review_passed(harness: Harness):
    commit = accept_development(harness, "TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", commit, "patch_required"))
    patch_result, patch_commit = harness.patch("TASK-LIGHT", commit)
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", patch_result)
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", patch_commit, "passed", patch_review=True))
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] == "accepted"
    assert task["acceptance_mode"] == "qoder_patch_review"
    assert task["patch_cycle_count"] == 1


def test_second_patch_required_stops_for_human(harness: Harness):
    commit = accept_development(harness, "TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", commit, "patch_required"))
    patch_result, patch_commit = harness.patch("TASK-LIGHT", commit)
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", patch_result)
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", patch_commit, "patch_required", patch_review=True))
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] == "human_intervention_required"
    assert task["final_status"] == "human_intervention_required"
    assert task["next_action"] == "stop"


def test_commit_mismatch_stops_transition(harness: Harness):
    result, _commit = harness.develop("TASK-LIGHT")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["delivery_commit"] = "f" * 40
    write_yaml(result, value)
    with pytest.raises(WorkflowError):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_schema_error_is_persisted(harness: Harness):
    result, _commit = harness.develop("TASK-LIGHT")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value.pop("batch_id")
    write_yaml(result, value)
    with pytest.raises(WorkflowError, match="batch_id"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] == "workflow_error"
    assert task["errors"][0]["code"] == "schema_validation_failed"


def test_retry_ingest_rejects_uncorrected_schema_without_mutation(harness: Harness):
    result, _commit = harness.develop("TASK-LIGHT")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["unexpected_metadata"] = True
    write_yaml(result, value)
    with pytest.raises(WorkflowError):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    state_before = harness.engine.state_path(BATCH_ID).read_bytes()
    events_before = harness.engine.events_path(BATCH_ID).read_bytes()
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == "schema_validation_failed"
    assert harness.engine.state_path(BATCH_ID).read_bytes() == state_before
    assert harness.engine.events_path(BATCH_ID).read_bytes() == events_before


def test_retry_ingest_corrected_result_reaches_review_pending(harness: Harness):
    result, delivery_commit, _digest = fail_development_schema_then_correct(harness)
    response = harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert response == {
        "duplicate": False,
        "result_type": "development_result",
        "recovery_performed": True,
        "previous_state": "workflow_error",
        "resolved_error_code": "schema_validation_failed",
        "result_ingested": True,
        "current_state": "review_pending",
        "next_action": "qoder_review",
    }
    assert task["delivery_commit"] == delivery_commit
    assert task["current_state"] == "review_pending"


def test_retry_review_result_patch_required_recovers_to_patch_pending(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    review = harness.review("TASK-LIGHT", delivery, "patch_required")
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", review)
    response = harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", review)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert response["result_type"] == "review_result"
    assert response["current_state"] == "patch_pending"
    assert response["next_action"] == "mimo_patch"
    assert task["open_issue_ids"] == ["ISSUE-001"]


def test_retry_review_result_passed_recovers_to_accepted(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    review = harness.review("TASK-LIGHT", delivery, "passed")
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", review)
    response = harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", review)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert response["current_state"] == "accepted"
    assert response["next_action"] == "task_accepted"
    assert task["acceptance_mode"] == "qoder_review"


def test_retry_review_result_rejects_reviewed_commit_mismatch(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    review = harness.review("TASK-LIGHT", delivery, "passed")
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", review)
    value = yaml.safe_load(review.read_text(encoding="utf-8"))
    value["reviewed_commit"] = harness.planning_commit
    write_yaml(review, value)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", review)
    assert caught.value.code == "review_commit_mismatch"
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_retry_patch_result_recovers_to_patch_review_pending(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", delivery, "patch_required"))
    patch_result, patch_commit = harness.patch("TASK-LIGHT", delivery)
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", patch_result)
    response = harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", patch_result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert response["result_type"] == "patch_result"
    assert response["current_state"] == "patch_review_pending"
    assert response["next_action"] == "qoder_patch_review"
    assert task["patch_commit"] == patch_commit


def test_retry_patch_result_rejects_changed_patch_commit(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", delivery, "patch_required"))
    patch_result, _patch_commit = harness.patch("TASK-LIGHT", delivery)
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", patch_result)
    value = yaml.safe_load(patch_result.read_text(encoding="utf-8"))
    value["patch_commit"] = delivery
    write_yaml(patch_result, value)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", patch_result)
    assert caught.value.code == "patch_commit_mismatch"


def test_retry_patch_result_rejects_patch_scope_mismatch(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", delivery, "patch_required"))
    patch_result, _patch_commit = harness.patch("TASK-LIGHT", delivery, unexpected=True)
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", patch_result)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", patch_result)
    assert caught.value.code == "patch_scope_mismatch"


def test_retry_ingest_rejects_failed_result_type_mismatch(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    review = harness.review("TASK-LIGHT", delivery, "passed")
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", review)
    development = harness.runtime / BATCH_ID / "TASK-LIGHT" / "development_result.yaml"
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", development)
    assert caught.value.code == "result_type_mismatch"


def test_retry_ingest_rejects_unknown_result_filename(harness: Harness):
    unknown = harness.incoming / "TASK-LIGHT" / "unknown_result.yaml"
    write_yaml(unknown, {"batch_id": BATCH_ID, "task_id": "TASK-LIGHT"})
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", unknown)
    assert caught.value.code == "retry_ingest_result_type_invalid"


def test_retry_review_result_is_idempotent(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    review = harness.review("TASK-LIGHT", delivery, "patch_required")
    fail_machine_result_schema_then_correct(harness, "TASK-LIGHT", review)
    harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", review)
    events_before = harness.engine.events_path(BATCH_ID).read_bytes()
    duplicate = harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", review)
    assert duplicate["duplicate"] is True
    assert duplicate["result_type"] == "review_result"
    assert duplicate["current_state"] == "patch_pending"
    assert harness.engine.events_path(BATCH_ID).read_bytes() == events_before


def test_retry_ingest_preserves_original_event_and_records_resolved_error(harness: Harness):
    result, _commit, original_digest = fail_development_schema_then_correct(harness)
    original_lines = harness.engine.events_path(BATCH_ID).read_text(encoding="utf-8").splitlines()
    corrected_digest = hashlib.sha256(result.read_bytes()).hexdigest()
    harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    final_lines = harness.engine.events_path(BATCH_ID).read_text(encoding="utf-8").splitlines()
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    audit = task["resolved_errors"][0]
    assert final_lines[:len(original_lines)] == original_lines
    assert any(json.loads(line)["event"] == "workflow_error_resolved" for line in final_lines)
    assert audit["code"] == "schema_validation_failed"
    assert audit["original_file_sha256"] == original_digest
    assert audit["corrected_file_sha256"] == corrected_digest
    assert audit["resolution"] == "corrected_machine_result_reingested"
    summary = harness.engine.write_summary(BATCH_ID)
    assert summary["counts"]["workflow_error"] == 0
    assert summary["resolved_error_count"] == 1
    assert summary["tasks"]["TASK-LIGHT"]["resolved_error_count"] == 1


def test_retry_ingest_persists_only_final_recovered_state(harness: Harness, monkeypatch: pytest.MonkeyPatch):
    result, _commit, _digest = fail_development_schema_then_correct(harness)
    persisted_states: list[str] = []
    original_persist = harness.engine._persist

    def capture_persist(state: dict[str, Any], events=()):
        persisted_states.append(state["tasks"]["TASK-LIGHT"]["current_state"])
        return original_persist(state, events)

    monkeypatch.setattr(harness.engine, "_persist", capture_persist)
    harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert persisted_states == ["review_pending"]


def test_retry_ingest_rejects_changed_planning_commit(harness: Harness):
    result, delivery_commit, _digest = fail_development_schema_then_correct(harness)
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["planning_commit"] = delivery_commit
    write_yaml(result, value)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == "planning_commit_mismatch"
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_retry_ingest_rejects_changed_delivery_commit(harness: Harness):
    result, _delivery_commit, _digest = fail_development_schema_then_correct(harness)
    metadata = harness.root / "metadata/other.txt"
    metadata.parent.mkdir()
    metadata.write_text("not the delivery\n", encoding="utf-8")
    run_git(harness.root, "add", "metadata/other.txt")
    run_git(harness.root, "commit", "-m", "metadata: unrelated")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["delivery_commit"] = run_git(harness.root, "rev-parse", "HEAD")
    write_yaml(result, value)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == "delivery_commit_mismatch"


def test_retry_ingest_rejects_delivery_scope_drift(harness: Harness):
    result, _commit, _digest = fail_development_schema_then_correct(harness, unexpected=True)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == "delivery_scope_mismatch"
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_retry_ingest_rejects_modified_planning_asset(harness: Harness):
    result, _commit, _digest = fail_development_schema_then_correct(harness)
    package = harness.root / "task_packages/TASK-LIGHT/task_package.yaml"
    package.write_text(package.read_text(encoding="utf-8") + "\n# changed after freeze\n", encoding="utf-8")
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == "planning_asset_modified"


@pytest.mark.parametrize(
    ("field", "wrong_value", "error_code"),
    [
        ("batch_id", "BATCH-WRONG", "batch_id_mismatch"),
        ("task_id", "TASK-WRONG", "task_id_mismatch"),
    ],
)
def test_retry_ingest_rejects_identity_mismatch(
    harness: Harness,
    field: str,
    wrong_value: str,
    error_code: str,
):
    result, _commit, _digest = fail_development_schema_then_correct(harness)
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value[field] = wrong_value
    write_yaml(result, value)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == error_code


def test_retry_ingest_same_corrected_file_is_idempotent(harness: Harness):
    result, _commit, _digest = fail_development_schema_then_correct(harness)
    harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    events_before = harness.engine.events_path(BATCH_ID).read_bytes()
    duplicate = harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert duplicate["duplicate"] is True
    assert duplicate["recovery_performed"] is False
    assert harness.engine.events_path(BATCH_ID).read_bytes() == events_before


def test_recovered_task_cannot_recover_same_error_with_different_file(harness: Harness):
    result, _commit, _digest = fail_development_schema_then_correct(harness)
    harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["artifacts"] = ["outputs/TASK-LIGHT.txt"]
    write_yaml(result, value)
    with pytest.raises(WorkflowError) as caught:
        harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    assert caught.value.code == "retry_ingest_state_invalid"


def test_retry_ingest_does_not_change_other_accepted_task(harness: Harness):
    accept_development(harness, "TASK-VALIDATOR")
    accepted_before = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    result, _commit, _digest = fail_development_schema_then_correct(harness)
    harness.engine.retry_ingest(BATCH_ID, "TASK-LIGHT", result)
    accepted_after = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    assert accepted_after == accepted_before
    assert accepted_after["current_state"] == "accepted"


def test_batch_006_synthetic_replay_recovers_to_review_pending(tmp_path: Path):
    batch_id = "BATCH-2026-07-20-006"
    task_id = "Phase-PATCH-FLOW-002"
    synthetic = Harness(
        tmp_path,
        profiles={task_id: "lightweight_non_execution"},
        batch_id=batch_id,
    )
    synthetic.init()
    result, delivery_commit, _digest = fail_development_schema_then_correct(synthetic, task_id)
    before = {
        str(path.relative_to(synthetic.runtime / batch_id)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (synthetic.runtime / batch_id).rglob("*") if path.is_file()
    }
    simulation = synthetic.engine.retry_ingest(batch_id, task_id, result, dry_run=True)
    after = {
        str(path.relative_to(synthetic.runtime / batch_id)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (synthetic.runtime / batch_id).rglob("*") if path.is_file()
    }
    assert before == after
    assert simulation["state_unchanged"] is True
    assert simulation["projected_current_state"] == "review_pending"
    synthetic.engine.retry_ingest(batch_id, task_id, result)
    task = synthetic.engine.load_state(batch_id)["tasks"][task_id]
    assert task["current_state"] == "review_pending"
    assert task["planning_commit"] == synthetic.planning_commit
    assert task["delivery_commit"] == delivery_commit


def test_current_batch_006_review_retry_dry_run_is_read_only():
    batch_id = "BATCH-2026-07-20-006"
    task_id = "Phase-PATCH-FLOW-002"
    engine = WorkflowEngine(PROJECT_ROOT)
    state_path = engine.state_path(batch_id)
    result = engine.batch_dir(batch_id) / task_id / "review_result.yaml"
    if not state_path.exists() or not result.exists():
        pytest.skip("Operational BATCH-006 runtime state is not present")
    state = engine.load_state(batch_id)
    task = state["tasks"][task_id]
    if (
        task["current_state"] != "workflow_error"
        or not task["errors"]
        or task["errors"][-1].get("failed_result_type") != "review_result"
    ):
        pytest.skip("Operational BATCH-006 is no longer at the review-result recovery checkpoint")
    batch_dir = engine.batch_dir(batch_id)
    before = {
        str(path.relative_to(batch_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in batch_dir.rglob("*") if path.is_file()
    }
    simulation = engine.retry_ingest(batch_id, task_id, result, dry_run=True)
    after = {
        str(path.relative_to(batch_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in batch_dir.rglob("*") if path.is_file()
    }
    assert before == after
    assert simulation["result_type"] == "review_result"
    assert simulation["projected_current_state"] == "patch_pending"
    assert simulation["next_action"] == "mimo_patch"
    assert engine.load_state(batch_id)["event_sequence"] == state["event_sequence"]


def test_validator_failure_does_not_accept_task(tmp_path: Path):
    harness = Harness(tmp_path, fail_validator_task="TASK-VALIDATOR")
    harness.init()
    result, _commit = harness.develop("TASK-VALIDATOR")
    harness.engine.ingest(BATCH_ID, "TASK-VALIDATOR", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    assert task["current_state"] == "validator_failed"
    assert task["final_status"] == "pending"


def test_validator_without_args_executes_and_records_full_command(harness: Harness):
    result, _commit = harness.develop("TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    execution = task["last_validator_execution"]
    assert execution["phase"] == "development"
    assert execution["args"] == []
    assert execution["resolved_command"] == [sys.executable, "validators/pass.py"]
    assert execution["exit_code"] == 0
    assert execution["stdout"] == ""
    assert execution["stderr"] == ""


def test_development_validator_receives_frozen_phase_args(tmp_path: Path):
    phase = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
    )
    phase.init()
    result, _commit = phase.develop("TASK-PHASE")
    phase.engine.ingest(BATCH_ID, "TASK-PHASE", result)
    execution = phase.engine.load_state(BATCH_ID)["tasks"]["TASK-PHASE"]["last_validator_execution"]
    assert execution["args"] == ["--phase", "development"]
    assert execution["resolved_command"] == [
        sys.executable, "validators/phase.py", "--phase", "development",
    ]
    assert execution["stdout"] == "phase=development\n"


def test_new_task_requires_all_three_structured_validator_phases(tmp_path: Path):
    phase = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
    )
    package_path = phase.root / "task_packages/TASK-PHASE/task_package.yaml"
    package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    package["validator_commands"].pop("planning")
    write_yaml(package_path, package)
    with pytest.raises(WorkflowError) as caught:
        phase.init()
    assert caught.value.code == "validator_phase_missing"


def test_patch_validator_uses_patch_phase_args(tmp_path: Path):
    phase = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
    )
    phase.init()
    delivery = accept_development(phase, "TASK-PHASE")
    phase.engine.ingest(BATCH_ID, "TASK-PHASE", phase.review("TASK-PHASE", delivery, "patch_required"))
    patch_result, _patch_commit = phase.patch("TASK-PHASE", delivery)
    phase.engine.ingest(BATCH_ID, "TASK-PHASE", patch_result)
    execution = phase.engine.load_state(BATCH_ID)["tasks"]["TASK-PHASE"]["last_validator_execution"]
    assert execution["phase"] == "patch"
    assert execution["args"] == ["--phase", "patch"]
    assert execution["stdout"] == "phase=patch\n"


def test_missing_frozen_validator_args_causes_failure(tmp_path: Path):
    phase = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
        validator_args_by_phase={"planning": [], "development": [], "patch": []},
    )
    phase.init()
    result, _commit = phase.develop("TASK-PHASE")
    phase.engine.ingest(BATCH_ID, "TASK-PHASE", result)
    task = phase.engine.load_state(BATCH_ID)["tasks"]["TASK-PHASE"]
    assert task["current_state"] == "validator_failed"
    assert task["last_validator_execution"]["exit_code"] == 2
    assert "--phase" in task["last_validator_execution"]["stderr"]


def test_agent_result_cannot_override_frozen_validator_args(tmp_path: Path):
    phase = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
    )
    phase.init()
    result, _commit = phase.develop("TASK-PHASE")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["validator_args"] = ["--phase", "patch"]
    write_yaml(result, value)
    with pytest.raises(WorkflowError) as caught:
        phase.engine.ingest(BATCH_ID, "TASK-PHASE", result)
    assert caught.value.code == "schema_validation_failed"
    assert phase.engine.load_state(BATCH_ID)["tasks"]["TASK-PHASE"]["last_validator_execution"] is None


def test_runtime_state_cannot_replace_frozen_validator_args(tmp_path: Path):
    phase = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
    )
    phase.init()
    state = phase.engine.load_state(BATCH_ID)
    command = state["tasks"]["TASK-PHASE"]["validator"]["commands"]["development"]
    command["args"] = ["--phase", "patch"]
    command["resolved_command"] = [sys.executable, "validators/phase.py", "--phase", "patch"]
    write_yaml(phase.engine.state_path(BATCH_ID), state)
    result, _commit = phase.develop("TASK-PHASE")
    with pytest.raises(WorkflowError) as caught:
        phase.engine.ingest(BATCH_ID, "TASK-PHASE", result)
    assert caught.value.code == "validator_runtime_override_rejected"
    task = phase.engine.load_state(BATCH_ID)["tasks"]["TASK-PHASE"]
    assert task["current_state"] == "workflow_error"
    assert task["last_validator_execution"] is None


def test_validator_shell_operator_is_rejected(tmp_path: Path):
    unsafe = Harness(
        tmp_path,
        profiles={"TASK-PHASE": "lightweight_non_execution"},
        phase_aware_validator=True,
        validator_args_by_phase={
            "planning": ["--phase", "planning"],
            "development": ["--phase", "development", ";"],
            "patch": ["--phase", "patch"],
        },
    )
    with pytest.raises(WorkflowError) as caught:
        unsafe.init()
    assert caught.value.code == "validator_shell_operator_rejected"


def test_validator_script_outside_repository_is_rejected(tmp_path: Path):
    harness = Harness(tmp_path)
    with pytest.raises(WorkflowError) as caught:
        harness.engine._structured_validator_command(
            {
                "executable": "python",
                "script": "../outside.py",
                "args": [],
                "timeout_seconds": 120,
            },
            "development",
        )
    assert caught.value.code == "validator_outside_project"


def test_rerun_validator_recovers_runner_defect_and_preserves_history(tmp_path: Path):
    batch_id = "BATCH-2026-07-20-007"
    task_id = "Phase-PATCH-FLOW-003"
    phase = Harness(
        tmp_path,
        profiles={task_id: "lightweight_non_execution"},
        batch_id=batch_id,
        phase_aware_validator=True,
    )
    phase.init()
    result, delivery = phase.develop(task_id)
    seed_legacy_validator_runner_failure(phase, task_id, result, delivery)
    failed_state = phase.engine.load_state(batch_id)
    assert failed_state["tasks"][task_id]["current_state"] == "validator_failed"
    original_events = phase.engine.events_path(batch_id).read_text(encoding="utf-8").splitlines()
    response = phase.engine.rerun_validator(batch_id, task_id)
    recovered = phase.engine.load_state(batch_id)
    task = recovered["tasks"][task_id]
    final_events = phase.engine.events_path(batch_id).read_text(encoding="utf-8").splitlines()
    assert final_events[:len(original_events)] == original_events
    assert response["failure_caused_by_runner_defect"] is True
    assert response["delivery_commit_unchanged"] is True
    assert response["current_state"] == "review_pending"
    assert response["next_action"] == "qoder_review"
    assert response["validator_execution"]["args"] == ["--phase", "development"]
    assert task["delivery_commit"] == delivery
    assert task["validator_status"] == "passed"
    assert task["resolved_errors"][-1]["error_category"] == "orchestrator_validator_invocation_defect"
    assert any(json.loads(line)["event"] == "validator_runner_defect_resolved" for line in final_events)


def test_batch_007_legacy_frozen_command_adapter_preserves_phase_args():
    engine = WorkflowEngine(PROJECT_ROOT)
    package_path = PROJECT_ROOT / "task_packages/Phase-PATCH-FLOW-003/task_package.yaml"
    if not package_path.exists():
        pytest.skip("BATCH-007 frozen task package is not present")
    package = yaml.safe_load(package_path.read_text(encoding="utf-8"))
    validator = engine._legacy_phase_validator(package)
    assert validator["commands"]["development"]["args"] == ["--phase", "development"]
    assert validator["commands"]["patch"]["args"] == ["--phase", "patch"]
    assert validator["commands"]["development"]["source_format"] == "legacy_frozen_phase_command_adapter"


def test_rerun_validator_does_not_change_other_accepted_task(tmp_path: Path):
    phase = Harness(tmp_path, phase_aware_validator=True)
    phase.init()
    accept_development(phase, "TASK-VALIDATOR")
    accepted_before = phase.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    result, delivery = phase.develop("TASK-LIGHT")
    seed_legacy_validator_runner_failure(phase, "TASK-LIGHT", result, delivery)
    phase.engine.rerun_validator(BATCH_ID, "TASK-LIGHT")
    accepted_after = phase.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    assert accepted_after == accepted_before


def test_rerun_validator_rejects_genuine_validator_failure(tmp_path: Path):
    failing = Harness(tmp_path, fail_validator_task="TASK-LIGHT")
    failing.init()
    result, _delivery = failing.develop("TASK-LIGHT")
    failing.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    with pytest.raises(WorkflowError) as caught:
        failing.engine.rerun_validator(BATCH_ID, "TASK-LIGHT")
    assert caught.value.code == "validator_failure_not_runner_defect"
    assert failing.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "validator_failed"


def test_scope_drift_is_rejected(harness: Harness):
    result, _commit = harness.develop("TASK-LIGHT", unexpected=True)
    with pytest.raises(WorkflowError, match="outside frozen scope"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] == "workflow_error"
    assert task["current_task_commit_scope_verified"] is None


def test_duplicate_ingest_is_idempotent(harness: Harness):
    result, _commit = harness.develop("TASK-VALIDATOR")
    first = harness.engine.ingest(BATCH_ID, "TASK-VALIDATOR", result)
    event_count = len(harness.engine.events_path(BATCH_ID).read_text(encoding="utf-8").splitlines())
    second = harness.engine.ingest(BATCH_ID, "TASK-VALIDATOR", result)
    assert first["duplicate"] is False
    assert second["duplicate"] is True
    assert len(harness.engine.events_path(BATCH_ID).read_text(encoding="utf-8").splitlines()) == event_count


def test_resume_regenerates_identical_current_handoff(harness: Harness):
    handoff = Path(harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["handoffs"]["development_pending"])
    before = handoff.read_text(encoding="utf-8")
    result = harness.engine.resume_batch(BATCH_ID)
    assert result["resumed"] is True
    assert handoff.read_text(encoding="utf-8") == before
    assert not (handoff.parent / "qoder_review_request.md").exists()


def test_batch_summary_aggregates_all_tasks(harness: Harness):
    accept_development(harness, "TASK-VALIDATOR")
    accept_review(harness, "TASK-LIGHT")
    accept_review(harness, "TASK-FULL")
    summary = harness.engine.write_summary(BATCH_ID)
    assert summary["counts"] == {
        "accepted": 3, "review_pending": 0, "patch_pending": 0,
        "human_intervention_required": 0, "workflow_error": 0,
    }
    assert summary["all_tasks_accepted"] is True
    assert summary["batch_ready_for_next_round"] is True


def test_full_planning_and_delivery_commits_pass_and_handoff_uses_full_hash(harness: Harness):
    assert len(harness.planning_commit) == 40
    delivery = accept_development(harness, "TASK-LIGHT")
    assert len(delivery) == 40
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    handoff = Path(task["handoffs"]["review_pending"]).read_text(encoding="utf-8")
    assert f"- planning_commit: {harness.planning_commit}" in handoff
    assert f"- delivery_commit: {delivery}" in handoff
    assert f"- reviewed_commit_expected: {delivery}" in handoff
    assert "metadata_commit_is_review_target: false" in handoff


def test_short_commit_is_rejected_for_init_and_development(tmp_path: Path):
    short_init = Harness(tmp_path / "init")
    with pytest.raises(WorkflowError) as init_error:
        short_init.engine.init_batch(BATCH_ID, short_init.planning_commit[:8])
    assert init_error.value.code == "full_commit_required"

    short_delivery = Harness(tmp_path / "delivery")
    short_delivery.init()
    result, _commit = short_delivery.develop("TASK-LIGHT")
    value = yaml.safe_load(result.read_text(encoding="utf-8"))
    value["delivery_commit"] = value["delivery_commit"][:8]
    write_yaml(result, value)
    with pytest.raises(WorkflowError, match="delivery_commit"):
        short_delivery.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    assert short_delivery.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_delivery_commit_is_reviewed_even_when_current_head_is_metadata(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    marker = harness.root / "metadata/review-preparation.txt"
    marker.parent.mkdir()
    marker.write_text("metadata only\n", encoding="utf-8")
    run_git(harness.root, "add", "metadata/review-preparation.txt")
    run_git(harness.root, "commit", "-m", "metadata: prepare review")
    assert run_git(harness.root, "rev-parse", "HEAD") != delivery
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", delivery))
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "accepted"


def test_handoff_commit_cannot_replace_delivery_commit(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    handoff = Path(task["handoffs"]["review_pending"])
    handoff_relative = str(handoff.relative_to(harness.root))
    run_git(harness.root, "add", handoff_relative)
    run_git(harness.root, "commit", "-m", "metadata: review handoff")
    handoff_commit = run_git(harness.root, "rev-parse", "HEAD")
    assert handoff_commit != delivery
    review = harness.review("TASK-LIGHT", delivery)
    value = yaml.safe_load(review.read_text(encoding="utf-8"))
    value["delivery_commit"] = handoff_commit
    value["reviewed_commit"] = handoff_commit
    write_yaml(review, value)
    with pytest.raises(WorkflowError, match="delivery_commit"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", review)


def test_development_result_metadata_commit_cannot_replace_delivery_commit(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    canonical = harness.runtime / BATCH_ID / "TASK-LIGHT" / "development_result.yaml"
    canonical_relative = str(canonical.relative_to(harness.root))
    run_git(harness.root, "add", canonical_relative)
    run_git(harness.root, "commit", "-m", "metadata: record development result")
    metadata_commit = run_git(harness.root, "rev-parse", "HEAD")
    assert metadata_commit != delivery
    review = harness.review("TASK-LIGHT", delivery)
    value = yaml.safe_load(review.read_text(encoding="utf-8"))
    value["delivery_commit"] = metadata_commit
    value["reviewed_commit"] = metadata_commit
    write_yaml(review, value)
    with pytest.raises(WorkflowError, match="delivery_commit"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", review)


def test_development_result_does_not_require_its_own_commit(harness: Harness):
    result, delivery = harness.develop("TASK-VALIDATOR")
    assert result.is_relative_to(harness.incoming)
    assert harness.engine._commit_files(delivery) == ["outputs/TASK-VALIDATOR.txt"]
    harness.engine.ingest(BATCH_ID, "TASK-VALIDATOR", result)
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    assert task["delivery_commit"] == delivery
    assert task["metadata_commit"] is None
    assert task["current_state"] == "accepted"


def test_qoder_reviewed_commit_must_match_delivery_commit(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    review = harness.review("TASK-LIGHT", delivery)
    value = yaml.safe_load(review.read_text(encoding="utf-8"))
    value["reviewed_commit"] = harness.planning_commit
    value["reviewed_commit_matches_delivery_commit"] = False
    write_yaml(review, value)
    with pytest.raises(WorkflowError, match="reviewed_commit"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", review)
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_patch_review_commit_mismatch_is_rejected(harness: Harness):
    delivery = accept_development(harness, "TASK-LIGHT")
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", harness.review("TASK-LIGHT", delivery, "patch_required"))
    patch_result, patch_commit = harness.patch("TASK-LIGHT", delivery)
    harness.engine.ingest(BATCH_ID, "TASK-LIGHT", patch_result)
    review = harness.review("TASK-LIGHT", patch_commit, "passed", patch_review=True)
    value = yaml.safe_load(review.read_text(encoding="utf-8"))
    value["reviewed_patch_commit"] = delivery
    write_yaml(review, value)
    with pytest.raises(WorkflowError, match="Patch review Commits"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", review)


def test_planning_asset_in_delivery_commit_fails_scope_check(harness: Harness):
    result, _delivery = harness.develop("TASK-LIGHT", include_planning_asset=True)
    with pytest.raises(WorkflowError, match="outside frozen scope"):
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result)
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]["current_state"] == "workflow_error"


def test_runtime_metadata_in_ancestry_is_not_counted_in_delivery_scope(harness: Harness):
    marker = harness.root / "runtime/metadata-before-delivery.yaml"
    marker.write_text("metadata: true\n", encoding="utf-8")
    run_git(harness.root, "add", "runtime/metadata-before-delivery.yaml")
    run_git(harness.root, "commit", "-m", "metadata: before delivery")
    metadata_commit = run_git(harness.root, "rev-parse", "HEAD")
    result, delivery = harness.develop("TASK-VALIDATOR")
    assert metadata_commit != delivery
    assert harness.engine._commit_files(delivery) == ["outputs/TASK-VALIDATOR.txt"]
    harness.engine.ingest(BATCH_ID, "TASK-VALIDATOR", result)
    assert harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]["current_state"] == "accepted"


def test_batch_005_negative_replay_stops_without_writes_or_patch_handoff():
    batch_id = "BATCH-2026-07-20-005"
    batch_dir = PROJECT_ROOT / "runtime" / batch_id
    before = {
        str(path.relative_to(batch_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in batch_dir.rglob("*") if path.is_file()
    }
    replay = WorkflowEngine(PROJECT_ROOT).replay_batch(batch_id)
    after = {
        str(path.relative_to(batch_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in batch_dir.rglob("*") if path.is_file()
    }
    assert before == after
    assert replay["final_state"] == "workflow_error"
    assert replay["error_categories"] == [
        "development_result_missing_delivery_commit",
        "short_commit_in_handoff",
        "review_result_schema_invalid",
        "planning_and_delivery_commit_not_separated",
    ]
    assert replay["patch_handoff_generated"] is False
    assert replay["historical_files_rewritten"] is False


@pytest.mark.parametrize(
    ("batch_id", "expected_count", "expected_all_accepted"),
    [
        ("BATCH-2026-07-20-001", 1, False),
        ("BATCH-2026-07-20-002", 1, True),
        ("BATCH-2026-07-20-003", 1, True),
        ("BATCH-2026-07-20-004", 3, False),
    ],
)
def test_historical_batches_replay_read_only(batch_id: str, expected_count: int, expected_all_accepted: bool):
    engine = WorkflowEngine(PROJECT_ROOT)
    batch_dir = PROJECT_ROOT / "runtime" / batch_id
    before = {
        str(path.relative_to(batch_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in batch_dir.rglob("*") if path.is_file()
    }
    replay = engine.replay_batch(batch_id)
    after = {
        str(path.relative_to(batch_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in batch_dir.rglob("*") if path.is_file()
    }
    assert before == after
    assert replay["read_only"] is True
    assert replay["summary"]["task_count"] == expected_count
    assert replay["summary"]["all_tasks_accepted"] is expected_all_accepted
    assert replay["summary"]["batch_ready_for_next_round"] is expected_all_accepted


def test_historical_batch_four_preserves_warnings_and_profiles():
    replay = WorkflowEngine(PROJECT_ROOT).replay_batch("BATCH-2026-07-20-004")
    tasks = replay["summary"]["tasks"]
    assert {value["review_profile"] for value in tasks.values()} == {
        "validator_only", "lightweight_non_execution", "full_execution"
    }
    assert replay["compatibility_mode_recorded"] is True
    assert replay["historical_files_modified"] is False
    assert replay["historical_results_overwritten"] is False
    assert replay["new_runs"] == {
        "require_batch_id": True,
        "require_full_commit": True,
        "historical_compatibility_adapter_allowed": False,
    }
    recoveries = replay["compatibility_recoveries"]
    assert len(recoveries) == 1
    assert recoveries[0]["category"] == "historical_manifest_parse_recovery"
    assert recoveries[0]["recovery_applied"] is True
    assert recoveries[0]["source_modified"] is False
    assert recoveries[0]["source_file"] == "runtime/BATCH-2026-07-20-004/batch_manifest.yaml"
    assert recoveries[0]["recovery_reason"]


# --- Validator name contract tests (machine-result validator_name must be exact basename with extension) ---


def test_development_handoff_contains_exact_validator_basename(harness: Harness):
    """Handoff must include validator_name with exact frozen basename (e.g. pass.py)."""
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    handoff_path = Path(task["handoffs"]["development_pending"])
    content = handoff_path.read_text(encoding="utf-8")
    # The frozen validator script is validators/pass.py → basename is pass.py
    assert "- validator_name: pass.py" in content


def test_development_handoff_validator_name_preserves_py_suffix(harness: Harness):
    """validator_name in handoff must retain the .py extension."""
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    handoff_path = Path(task["handoffs"]["development_pending"])
    content = handoff_path.read_text(encoding="utf-8")
    # Must end with .py, not just stem
    assert "validator_name: pass.py" in content
    assert "validator_name: pass\n" not in content


def test_development_handoff_validator_name_has_no_directory_prefix(harness: Harness):
    """validator_name must be basename only, no validators/ prefix."""
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-VALIDATOR"]
    handoff_path = Path(task["handoffs"]["development_pending"])
    content = handoff_path.read_text(encoding="utf-8")
    assert "validator_name: validators/pass.py" not in content
    assert "validator_name: pass.py" in content


def test_ingest_with_exact_validator_name_transitions_to_review_pending(harness: Harness):
    """development_result with exact validator_name (pass.py) ingests successfully."""
    result_file, commit = harness.develop("TASK-LIGHT")
    outcome = harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result_file)
    assert outcome["duplicate"] is False
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] == "review_pending"
    assert task["delivery_commit"] == commit
    assert task["validator_status"] == "passed"


def test_ingest_with_stem_only_validator_name_is_rejected(harness: Harness):
    """development_result with stem-only validator_name (pass, no .py) must be rejected."""
    result_file, commit = harness.develop("TASK-LIGHT")
    # Tamper: replace validator_name with stem only
    raw = yaml.safe_load(result_file.read_text(encoding="utf-8"))
    raw["validator_name"] = "pass"  # stem only, missing .py
    result_file.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    with pytest.raises(WorkflowError) as exc_info:
        harness.engine.ingest(BATCH_ID, "TASK-LIGHT", result_file)
    assert exc_info.value.code == "validator_mismatch"
    # Task must NOT have transitioned to review_pending
    task = harness.engine.load_state(BATCH_ID)["tasks"]["TASK-LIGHT"]
    assert task["current_state"] != "review_pending"
