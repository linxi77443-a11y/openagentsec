#!/usr/bin/env python3
"""OpenAgentSec Command Line Interface (CLI).

Standard entry point for running AI security evaluations, listing capability modules,
and generating compliance scorecards.

Result semantics follow PRD v3.2 §13.1:
    PASS, FAIL, INCONCLUSIVE, BLOCKED, ERROR, NOT_FOUND

Exit codes:
    0 = PASS
    1 = NOT_FOUND
    2 = FAIL
    3 = BLOCKED
    4 = INCONCLUSIVE
    5 = ERROR

Only PASS returns 0.  A result is only trusted (PASS/FAIL) when it satisfies the
minimal result contract (PRD v3.2 §13.3 subset) and its evidence/artifacts verify.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

from src.openagentsec import __version__
from src.openagentsec.result_contract import (
    PASS,
    FAIL,
    NOT_FOUND,
    BLOCKED,
    INCONCLUSIVE,
    ERROR,
    ResultContract,
    contract_fields_complete,
    is_sha256_hex,
    resolve_status,
    sha256_hex,
    REASON_UNREGISTERED,
    REASON_NO_RESULT,
    REASON_AMBIGUOUS_RESULT_SET,
    REASON_UNTRUSTED_LEGACY_RESULT,
    REASON_INCOMPLETE_RESULT_CONTRACT,
    REASON_MODULE_ID_MISMATCH,
    REASON_EMPTY_RESULT,
    REASON_PARSE_ERROR,
    REASON_NOT_A_MAPPING,
    REASON_EVIDENCE_MISSING,
    REASON_EVIDENCE_NOT_HASH_BOUND,
    REASON_ARTIFACT_MISSING,
    REASON_PATH_ESCAPE,
    REASON_INVALID_HASH_FORMAT,
    REASON_HASH_MISMATCH,
    REASON_CONFLICTING_STATUS_FIELDS,
    REASON_REGISTRY_NOT_FOUND,
    REASON_REGISTRY_PARSE_ERROR,
    REASON_LEGACY_NONCANONICAL_RESULT,
    resolve_legacy_status,
)
from src.openagentsec.preflight import run_preflight
from src.openagentsec.version import PRODUCT_PRD_VERSION, software_version, get_git_commit

ROOT = Path(__file__).resolve().parents[2]

# git commit of the repository this CLI runs from (local, non-network).
_GIT_COMMIT = get_git_commit(ROOT)

# ---------------------------------------------------------------------------
# exit codes (aligned with PRD v3.2 §13.1)
# ---------------------------------------------------------------------------
EXIT_PASS = 0
EXIT_NOT_FOUND = 1
EXIT_FAIL = 2
EXIT_BLOCKED = 3
EXIT_INCONCLUSIVE = 4
EXIT_ERROR = 5

STATUS_EXIT = {
    "PASS": EXIT_PASS,
    "NOT_FOUND": EXIT_NOT_FOUND,
    "FAIL": EXIT_FAIL,
    "BLOCKED": EXIT_BLOCKED,
    "INCONCLUSIVE": EXIT_INCONCLUSIVE,
    "ERROR": EXIT_ERROR,
}

VALID_STATUSES = frozenset(STATUS_EXIT)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _load_registry() -> tuple[Optional[dict], Optional[str], Optional[str]]:
    """Return ``(registry_data, error_message, reason_code)``.

    Registry parse/read failures are returned structurally (never raised), so
    callers can produce a structured ERROR instead of an uncaught traceback.
    """
    registry_path = ROOT / "capability_modules" / "module_registry.yaml"
    if not registry_path.is_file():
        return None, "registry file not found", REASON_REGISTRY_NOT_FOUND
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except OSError as exc:
        return None, f"cannot read registry file: {exc}", REASON_REGISTRY_PARSE_ERROR
    except yaml.YAMLError as exc:
        return None, f"registry YAML parse error: {exc}", REASON_REGISTRY_PARSE_ERROR
    if not isinstance(data, dict):
        return None, "registry is not a mapping", REASON_REGISTRY_PARSE_ERROR
    return data, None, None


def _find_module_in_registry(module_id: str, reg: Optional[dict] = None) -> Optional[dict]:
    if reg is None:
        reg, _, _ = _load_registry()
    if not reg:
        return None
    for m in reg.get("modules", []):
        if m.get("module_id", "").upper() == module_id.upper():
            return m
    return None


def _find_result_files_in_dir(exec_dir: Path, mid: str) -> list:
    """Return existing result files for *mid* inside a single execution dir.

    YAML and JSON result files are both discovered and parsed through the same
    contract pipeline.  ``execution_results.json`` (historical naming) is
    intentionally out of scope for this round.
    """
    found = []
    for candidate in [
        exec_dir / "result.yaml",
        exec_dir / f"{mid}_result.yaml",
        exec_dir / "result.json",
        exec_dir / f"{mid}_result.json",
    ]:
        if candidate.is_file():
            found.append(candidate)
    return found


def _collect_candidate_results(module_id: str) -> list:
    """Collect all candidate result files for *module_id* under executions/.

    Directory-name containment is only used as a discovery heuristic; the final
    authority is the ``module_id`` declared inside each result file.
    """
    exec_root = ROOT / "executions"
    if not exec_root.is_dir():
        return []
    mid = module_id.lower()
    seen = set()
    candidates = []
    for p in sorted(exec_root.glob(f"*{mid}*")):
        if not p.is_dir():
            continue
        for r in _find_result_files_in_dir(p, mid):
            resolved = r.resolve()
            if resolved not in seen:
                seen.add(resolved)
                candidates.append(r)
    return candidates


def _load_result(result_path: Path) -> tuple[Optional[dict], Optional[str], Optional[str]]:
    """Return ``(parsed_data, error_message, reason_code)``.

    error_message is None on success.
    """
    try:
        raw = result_path.read_text(encoding="utf-8").strip()
        if not raw:
            return None, "result file is empty", REASON_EMPTY_RESULT
    except OSError as exc:
        return None, f"cannot read result file: {exc}", REASON_PARSE_ERROR
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        return None, f"YAML parse error: {exc}", REASON_PARSE_ERROR
    if data is None:
        return None, "result file is empty (parsed to None)", REASON_EMPTY_RESULT
    if not isinstance(data, dict):
        return None, f"result file is not a mapping (got {type(data).__name__})", REASON_NOT_A_MAPPING
    return data, None, None


def _opt_str(value) -> Optional[str]:
    return value if isinstance(value, str) else None


def _resolve_ref(ref, run_dir: Path) -> Optional[Path]:
    """Resolve an evidence/artifact reference safely.

    Absolute paths are rejected this round (no repo-level allowlist yet).
    Relative paths must not contain ``..`` and, after symlink resolution, the
    final realpath must remain inside the realpath of the run directory.
    """
    if not isinstance(ref, (str, Path)):
        return None
    p = Path(str(ref))
    if p.is_absolute():
        return None
    if ".." in p.parts:
        return None
    run_dir_real = os.path.realpath(run_dir)
    candidate = os.path.realpath(run_dir / p)
    if candidate == run_dir_real or candidate.startswith(run_dir_real + os.sep):
        return Path(candidate)
    return None


def _contract_from_data(data: dict, status: str, module_id: str) -> ResultContract:
    return ResultContract(
        status=status,
        module_id=module_id,
        run_id=_opt_str(data.get("run_id")),
        assessment_mode=_opt_str(data.get("assessment_mode")),
        maturity_level=_opt_str(data.get("maturity_level")),
        code_version=_opt_str(data.get("code_version")),
        evaluator_version=_opt_str(data.get("evaluator_version")),
        evidence_refs=data.get("evidence_refs"),
        artifact_hashes=data.get("artifact_hashes"),
        evaluation_status=status,
        product_prd_version=PRODUCT_PRD_VERSION,
        software_version=software_version(),
        git_commit=_GIT_COMMIT,
        raw=data,
    )


def _verify_evidence_and_hashes(rc: ResultContract, run_dir: Path) -> Optional[ResultContract]:
    """Verify evidence refs exist, are hash-bound, and artifact hashes match.

    None on success.
    """
    artifact_keys = {
        os.path.normpath(str(key)) for key in (rc.artifact_hashes or {}).keys()
    }
    for ref in rc.evidence_refs or []:
        resolved = _resolve_ref(ref, run_dir)
        if resolved is None:
            return ResultContract(
                status=ERROR, reason_code=REASON_PATH_ESCAPE,
                message=f"evidence ref {ref!r} escapes allowed scope", module_id=rc.module_id,
            )
        if not resolved.is_file():
            return ResultContract(
                status=ERROR, reason_code=REASON_EVIDENCE_MISSING,
                message=f"evidence file not found: {ref!r}", module_id=rc.module_id,
            )
        norm_ref = os.path.normpath(str(ref))
        if norm_ref not in artifact_keys:
            return ResultContract(
                status=ERROR, reason_code=REASON_EVIDENCE_NOT_HASH_BOUND,
                message=f"evidence ref {ref!r} is not bound to an artifact hash",
                module_id=rc.module_id,
            )

    for ref, digest in (rc.artifact_hashes or {}).items():
        resolved = _resolve_ref(ref, run_dir)
        if resolved is None:
            return ResultContract(
                status=ERROR, reason_code=REASON_PATH_ESCAPE,
                message=f"artifact ref {ref!r} escapes allowed scope", module_id=rc.module_id,
            )
        if not resolved.is_file():
            return ResultContract(
                status=ERROR, reason_code=REASON_ARTIFACT_MISSING,
                message=f"artifact file not found: {ref!r}", module_id=rc.module_id,
            )
        if not is_sha256_hex(digest):
            return ResultContract(
                status=ERROR, reason_code=REASON_INVALID_HASH_FORMAT,
                message=f"invalid SHA-256 format for artifact {ref!r}", module_id=rc.module_id,
            )
        try:
            actual = sha256_hex(resolved)
        except OSError as exc:
            return ResultContract(
                status=ERROR, reason_code=REASON_PARSE_ERROR,
                message=f"cannot hash artifact {ref!r}: {exc}", module_id=rc.module_id,
            )
        if actual.lower() != str(digest).lower():
            return ResultContract(
                status=ERROR, reason_code=REASON_HASH_MISMATCH,
                message=f"SHA-256 mismatch for artifact {ref!r}", module_id=rc.module_id,
            )
    return None


def _load_single_result(module_id: str, result_path: Path) -> ResultContract:
    """Strictly validate a single candidate result and build its contract."""
    run_dir = result_path.parent

    data, err, reason = _load_result(result_path)
    if err:
        return ResultContract(status=ERROR, reason_code=reason, message=err, module_id=module_id)

    data_module_id = data.get("module_id")
    if not (isinstance(data_module_id, str) and data_module_id.strip()):
        return ResultContract(
            status=INCONCLUSIVE, reason_code=REASON_INCOMPLETE_RESULT_CONTRACT,
            message="result file does not declare a module_id", module_id=module_id,
        )
    if data_module_id.upper() != module_id:
        return ResultContract(
            status=ERROR, reason_code=REASON_MODULE_ID_MISMATCH,
            message=f"result module_id {data_module_id!r} does not match queried module {module_id!r}",
            module_id=module_id,
        )

    status, status_key = resolve_status(data)
    rc = _contract_from_data(data, status, module_id)

    if status == ERROR and status_key == REASON_CONFLICTING_STATUS_FIELDS:
        rc.reason_code = REASON_CONFLICTING_STATUS_FIELDS
        rc.message = (
            "Conflicting status fields in result "
            "(final_status/status/evaluation_verdict disagree)."
        )
        return rc

    if status == ERROR and status_key is None:
        legacy = resolve_legacy_status(data)
        if legacy is not None:
            # Legacy non-canonical statuses (closed/judge_approved, *_VALIDATED,
            # VERDICT_*_CERTIFIED, released, certified, verified) are source
            # metadata only and are never mapped onto a canonical PASS.
            rc = ResultContract(
                status=INCONCLUSIVE,
                reason_code=REASON_LEGACY_NONCANONICAL_RESULT,
                message=(
                    f"Result carries only non-canonical legacy status {legacy!r}; "
                    "not mapped to PASS/FAIL."
                ),
                module_id=module_id,
                legacy_source_status=legacy,
                evaluation_status=INCONCLUSIVE,
                artifact_status="unverified",
            )
            rc.raw = data
            return rc
        rc.reason_code = REASON_INCOMPLETE_RESULT_CONTRACT
        rc.message = (
            "Result file has no usable status field "
            "(final_status/status/evaluation_verdict)."
        )
        return rc

    # Legacy-only status source: never auto-upgrade to a trusted PASS/FAIL.
    if status_key == "evaluation_verdict":
        rc.status = INCONCLUSIVE
        rc.reason_code = REASON_UNTRUSTED_LEGACY_RESULT
        rc.artifact_status = "unverified"
        rc.message = (
            "Result status is derived only from legacy evaluation_verdict; "
            "refusing to auto-upgrade to a trusted PASS/FAIL."
        )
        return rc

    if status not in (PASS, FAIL):
        if rc.reason_code is None:
            rc.reason_code = f"STATUS_{status}"
            rc.message = f"Result file declares status {status}."
        return rc

    if not contract_fields_complete(rc):
        rc.status = INCONCLUSIVE
        rc.reason_code = REASON_INCOMPLETE_RESULT_CONTRACT
        rc.artifact_status = "incomplete"
        rc.message = (
            "Result cannot be trusted: missing required contract fields "
            "(run_id, code_version, evaluator_version, evidence_refs, artifact_hashes)."
        )
        return rc

    verify = _verify_evidence_and_hashes(rc, run_dir)
    if verify is not None:
        verify.artifact_status = verify.reason_code or "unverified"
        return verify

    rc.artifact_status = "verified"
    return rc


def _resolve_module(module_id: str) -> ResultContract:
    """Resolve a module to a trusted result per PRD v3.2 §7.3 rules."""
    module_id = str(module_id).strip().upper()

    # 1. Registry existence (registry errors are structured, never raised)
    reg, reg_err, reg_reason = _load_registry()
    if reg_err:
        return ResultContract(
            status=ERROR, reason_code=reg_reason,
            message=reg_err, module_id=module_id,
        )
    if reg is None:
        return ResultContract(
            status=ERROR, reason_code=REASON_REGISTRY_NOT_FOUND,
            message="Registry file not found", module_id=module_id,
        )
    if _find_module_in_registry(module_id, reg) is None:
        return ResultContract(
            status=NOT_FOUND, reason_code=REASON_UNREGISTERED,
            message=f"Module {module_id} is not registered.", module_id=module_id,
        )

    # 2. Candidate results
    candidates = _collect_candidate_results(module_id)
    if not candidates:
        return ResultContract(
            status=NOT_FOUND, reason_code=REASON_NO_RESULT,
            message=f"No execution results for module {module_id}.", module_id=module_id,
        )

    # 3. Multiple candidates without an explicit run_id selection -> INCONCLUSIVE
    if len(candidates) > 1:
        paths = [str(c) for c in sorted(candidates)]
        return ResultContract(
            status=INCONCLUSIVE, reason_code=REASON_AMBIGUOUS_RESULT_SET,
            message=(
                f"Multiple candidate results for module {module_id}: {paths}. "
                "No explicit run_id selection; refusing to auto-select."
            ),
            module_id=module_id,
        )

    # 4. Single candidate -> strict contract validation
    return _load_single_result(module_id, candidates[0])


def _print_eval_result(rc: ResultContract) -> None:
    print(f"[{rc.status}] Module: {rc.module_id or 'unknown'}")
    if rc.reason_code:
        print(f"    reason_code:         {rc.reason_code}")
    if rc.message:
        print(f"    message:             {rc.message}")
    if rc.run_id:
        print(f"    run_id:              {rc.run_id}")
    if rc.code_version:
        print(f"    code_version:        {rc.code_version}")
    if rc.evaluator_version:
        print(f"    evaluator_version:   {rc.evaluator_version}")
    if rc.assessment_mode:
        print(f"    assessment_mode:     {rc.assessment_mode}")
    if rc.maturity_level:
        print(f"    maturity_level:      {rc.maturity_level}")
    if rc.evidence_refs:
        print(f"    evidence_refs:       {rc.evidence_refs}")
    if rc.artifact_hashes:
        print(f"    artifact_hashes:     {rc.artifact_hashes}")

    raw = rc.raw or {}
    if isinstance(raw, dict):
        total_cases = raw.get("total_cases")
        if total_cases is not None:
            print(f"    total_cases:         {total_cases}")
        breakthroughs = raw.get("breakthrough_detected_count")
        if breakthroughs is not None:
            print(f"    breakthroughs:       {breakthroughs}")
        synthetic_only = raw.get("synthetic_only")
        if isinstance(synthetic_only, bool):
            print(f"    synthetic_only:      {'true' if synthetic_only else 'false'}")
        elif synthetic_only is not None:
            print(f"    synthetic_only:      {synthetic_only}")
        else:
            print(f"    synthetic_only:      unknown")


# ---------------------------------------------------------------------------
# commands
# ---------------------------------------------------------------------------

def list_modules(reg: Optional[dict] = None) -> list[dict]:
    """List all registered security evaluation capability modules."""
    if reg is None:
        reg, reg_err, _ = _load_registry()
        if reg_err:
            print(f"[ERROR] {reg_err}", file=sys.stderr)
            return []
    if not reg:
        print("Error: Registry file not found", file=sys.stderr)
        return []

    modules = reg.get("modules", [])
    print(f"OpenAgentSec v{__version__} — Registered Security Modules ({len(modules)} total):")
    print("-" * 75)
    print(f"{'Module ID':<12} {'Priority':<10} {'Layer':<12} {'Status':<18} {'Name'}")
    print("-" * 75)
    for mod in modules:
        m_id = mod.get("module_id", "N/A")
        pri = mod.get("priority", "N/A")
        layer = mod.get("layer", "N/A")
        cov = mod.get("coverage", {}).get("coverage_status", mod.get("current_status", "N/A"))
        name = mod.get("module_name", "N/A")
        print(f"{m_id:<12} {pri:<10} {layer:<12} {cov:<18} {name}")
    print("-" * 75)
    return modules


def eval_module(target_module: str) -> int:
    """Run synthetic evaluation for a specific security module.

    Returns an exit code per PRD v3.2 §13.1 semantics.  Only PASS returns 0.
    """
    module_id = target_module.strip().upper()
    print(f"[*] OpenAgentSec: Querying module {module_id}", file=sys.stderr)
    rc = _resolve_module(module_id)
    _print_eval_result(rc)
    return STATUS_EXIT.get(rc.status, EXIT_ERROR)


@dataclass
class AuditResult:
    """Structured audit census derived from trusted run results (not registry)."""

    total_modules: int = 0
    pass_count: int = 0
    fail_count: int = 0
    blocked_count: int = 0
    inconclusive_count: int = 0
    error_count: int = 0
    not_found_count: int = 0
    no_trusted_result_count: int = 0
    overall_status: str = INCONCLUSIVE
    verdict: str = "implementation_in_progress"
    framework: str = "OpenAgentSec"
    version: str = __version__
    reason_code: Optional[str] = None
    message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "framework": self.framework,
            "version": self.version,
            "total_modules": self.total_modules,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "blocked_count": self.blocked_count,
            "inconclusive_count": self.inconclusive_count,
            "error_count": self.error_count,
            "not_found_count": self.not_found_count,
            "no_trusted_result_count": self.no_trusted_result_count,
            "overall_status": self.overall_status,
            "verdict": self.verdict,
            "reason_code": self.reason_code,
            "message": self.message,
        }


def _audit_overall(audit: AuditResult) -> str:
    """Aggregate overall audit status (fail-closed, never optimistic).

    Priority: any ERROR -> ERROR; any FAIL -> FAIL; any BLOCKED -> BLOCKED;
    no trusted results -> INCONCLUSIVE; any INCONCLUSIVE/NOT_FOUND -> INCONCLUSIVE;
    only when every module has a trusted PASS is the overall status PASS.
    """
    if audit.total_modules == 0:
        return INCONCLUSIVE
    if audit.error_count:
        return ERROR
    if audit.fail_count:
        return FAIL
    if audit.blocked_count:
        return BLOCKED
    if audit.pass_count + audit.fail_count == 0:
        return INCONCLUSIVE
    if audit.inconclusive_count or audit.not_found_count:
        return INCONCLUSIVE
    if audit.pass_count == audit.total_modules:
        return PASS
    return INCONCLUSIVE


def _run_audit() -> AuditResult:
    """Census every registry module using the same trusted-result resolution as eval."""
    reg, reg_err, reg_reason = _load_registry()
    audit = AuditResult()
    if reg_err:
        audit.overall_status = ERROR
        audit.reason_code = reg_reason
        audit.message = reg_err
        return audit
    if reg is None:
        audit.overall_status = ERROR
        audit.reason_code = REASON_REGISTRY_NOT_FOUND
        audit.message = "Registry file not found"
        return audit

    modules = reg.get("modules", [])
    audit.total_modules = len(modules)
    for mod in modules:
        module_id = mod.get("module_id")
        if not isinstance(module_id, str) or not module_id.strip():
            audit.error_count += 1
            continue
        status = _resolve_module(module_id).status
        if status == PASS:
            audit.pass_count += 1
        elif status == FAIL:
            audit.fail_count += 1
        elif status == BLOCKED:
            audit.blocked_count += 1
        elif status == INCONCLUSIVE:
            audit.inconclusive_count += 1
        elif status == ERROR:
            audit.error_count += 1
        else:
            audit.not_found_count += 1

    audit.no_trusted_result_count = audit.total_modules - (audit.pass_count + audit.fail_count)
    audit.overall_status = _audit_overall(audit)
    return audit


def audit_summary(output_format: str = "text", audit: Optional[AuditResult] = None) -> str:
    """Render the structured audit census.  Returns the rendered string only.

    The exit code is decided by the caller from ``audit.overall_status``; this
    function never mixes string and exit-code semantics.
    """
    if audit is None:
        audit = _run_audit()
    data = audit.to_dict()

    if output_format == "json":
        return json.dumps(data, indent=2)
    if output_format == "yaml":
        return yaml.dump(data, default_flow_style=False)

    lines = ["=" * 60]
    lines.append(f"OpenAgentSec v{__version__} Security Audit Summary")
    lines.append("=" * 60)
    for k, v in data.items():
        lines.append(f"  {k:<24}: {v}")
    lines.append("=" * 60)
    return "\n".join(lines)


def run_preflight_command(config_path: str) -> int:
    """Run the ten-dimension environment preflight gate from a YAML config.

    Fail-closed: BLOCKED / FAIL / INCONCLUSIVE / ERROR all return a non-zero
    exit code and must never continue execution.
    """
    path = Path(config_path)
    if not path.is_file():
        print(f"[ERROR] preflight config not found: {config_path}", file=sys.stderr)
        return EXIT_ERROR
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"[ERROR] cannot read preflight config: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except yaml.YAMLError as exc:
        print(f"[ERROR] preflight config parse error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    if not isinstance(data, dict):
        print("[ERROR] preflight config must be a YAML mapping", file=sys.stderr)
        return EXIT_ERROR

    result = run_preflight(data, root=path.parent)
    print(json.dumps(result.to_dict(), indent=2))
    preflight_exit = {
        PASS: EXIT_PASS,
        FAIL: EXIT_FAIL,
        BLOCKED: EXIT_BLOCKED,
        INCONCLUSIVE: EXIT_INCONCLUSIVE,
        ERROR: EXIT_ERROR,
    }
    return preflight_exit.get(result.overall, EXIT_INCONCLUSIVE)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="openagentsec",
        description="OpenAgentSec — Enterprise AI Security & Safety Assessment Workbench CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command: list-modules
    subparsers.add_parser("list-modules", help="List all registered AI security modules")

    # Command: eval
    eval_parser = subparsers.add_parser("eval", help="Run evaluation for a target module")
    eval_parser.add_argument("--target", "-t", required=True, help="Module ID (e.g. M48, M24, M25)")

    # Command: audit
    audit_parser = subparsers.add_parser("audit", help="Generate platform security audit report")
    audit_parser.add_argument(
        "--report", "-r", choices=["text", "json", "yaml"], default="text", help="Output format"
    )

    # Command: preflight
    preflight_parser = subparsers.add_parser(
        "preflight", help="Run the ten-dimension environment preflight gate (fail-closed)"
    )
    preflight_parser.add_argument(
        "--config", "-c", required=True, help="Path to a YAML preflight configuration"
    )

    args = parser.parse_args(argv)

    if args.command == "list-modules":
        reg, reg_err, _ = _load_registry()
        if reg_err:
            print(f"[ERROR] {reg_err}", file=sys.stderr)
            return EXIT_ERROR
        list_modules(reg)
        return 0
    elif args.command == "eval":
        return eval_module(args.target)
    elif args.command == "audit":
        audit = _run_audit()
        print(audit_summary(args.report, audit=audit))
        return STATUS_EXIT.get(audit.overall_status, EXIT_ERROR)
    elif args.command == "preflight":
        return run_preflight_command(args.config)
    else:
        parser.print_help()
        return 0


def eval_main() -> int:
    """Dedicated entry point for openagentsec-eval."""
    parser = argparse.ArgumentParser(prog="openagentsec-eval", description="Run OpenAgentSec security evaluation")
    parser.add_argument("target", help="Module ID to evaluate (e.g. M48, M24, M25)")
    args = parser.parse_args()
    return eval_module(args.target)


if __name__ == "__main__":
    sys.exit(main())
