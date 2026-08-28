#!/usr/bin/env python3
"""CLI for the deterministic task workflow orchestrator V0.2."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflow_orchestrator import WorkflowEngine, WorkflowError  # noqa: E402
from workflow_orchestrator.agent_executor import AgentExecutor  # noqa: E402


def emit(value: Any) -> None:
    if isinstance(value, (dict, list)):
        print(yaml.safe_dump(value, allow_unicode=True, sort_keys=False).rstrip())
    else:
        print(value)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Deterministic task workflow orchestrator V0.2")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init")
    init.add_argument("--batch", required=True)
    init.add_argument("--planning-commit", required=True)

    for name in ("status", "validate", "next", "summary", "resume", "replay", "split"):
        command = commands.add_parser(name)
        command.add_argument("--batch", required=True)

    ingest = commands.add_parser("ingest")
    ingest.add_argument("--batch", required=True)
    ingest.add_argument("--task", required=True)
    ingest.add_argument("--file", required=True, type=Path)
    retry = commands.add_parser("retry-ingest")
    retry.add_argument("--batch", required=True)
    retry.add_argument("--task", required=True)
    retry.add_argument("--file", required=True, type=Path)
    retry.add_argument("--dry-run", action="store_true")
    rerun_validator = commands.add_parser("rerun-validator")
    rerun_validator.add_argument("--batch", required=True)
    rerun_validator.add_argument("--task", required=True)
    commands.add_parser("agent-status")
    run_agent = commands.add_parser("run-agent")
    run_agent.add_argument("--batch", required=True)
    run_agent.add_argument("--task", required=True)
    approval = run_agent.add_mutually_exclusive_group(required=True)
    approval.add_argument("--dry-run", action="store_true")
    approval.add_argument("--approve", action="store_true")
    cancel_agent = commands.add_parser("cancel-agent")
    cancel_agent.add_argument("--batch", required=True)
    cancel_agent.add_argument("--task", required=True)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    engine = WorkflowEngine(PROJECT_ROOT)
    try:
        if args.command == "init":
            state = engine.init_batch(args.batch, args.planning_commit)
            emit({"batch_id": args.batch, "batch_state": state["batch_state"], "task_count": len(state["tasks"])})
        elif args.command == "status":
            emit(engine.load_state(args.batch))
        elif args.command == "validate":
            emit(engine.validate_batch(args.batch))
        elif args.command == "next":
            emit({"batch_id": args.batch, "handoffs": engine.next_handoffs(args.batch)})
        elif args.command == "ingest":
            emit(engine.ingest(args.batch, args.task, args.file))
        elif args.command == "retry-ingest":
            emit(engine.retry_ingest(args.batch, args.task, args.file, dry_run=args.dry_run))
        elif args.command == "rerun-validator":
            emit(engine.rerun_validator(args.batch, args.task))
        elif args.command == "agent-status":
            emit(AgentExecutor(engine).agent_status())
        elif args.command == "run-agent":
            executor = AgentExecutor(engine)
            if args.dry_run:
                emit(executor.dry_run(args.batch, args.task))
            else:
                result = executor.run_agent(args.batch, args.task, approved=True)
                emit(result)
                return 0 if result["error"] is None else 2
        elif args.command == "cancel-agent":
            emit(AgentExecutor(engine).cancel_agent(args.batch, args.task))
        elif args.command == "summary":
            summary = engine.write_summary(args.batch)
            emit({"path": str(engine.summary_path(args.batch)), "summary": summary})
        elif args.command == "resume":
            emit(engine.resume_batch(args.batch))
        elif args.command == "replay":
            emit(engine.replay_batch(args.batch))
        elif args.command == "split":
            emit(engine.split_manifest_batch(args.batch))
        else:
            raise AssertionError(args.command)
        return 0
    except WorkflowError as exc:
        payload = exc.as_dict()
        payload["error"] = payload.pop("code")
        print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
