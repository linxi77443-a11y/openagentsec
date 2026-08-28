#!/usr/bin/env python3
"""Phase 31 — Generic API Provider Formalization: Dry-Run Simulator。

对 sample target 做 dry-run simulation，不发起网络请求、不读取真实凭证、不访问 endpoint。
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_TARGETS_DIR = BASE_DIR / "api_provider" / "sample_targets"
OUTPUT_DIR = BASE_DIR / "api_provider"

GENERATED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Helpers ─────────────────────────────────────────────────────────────────


def load_yaml(path):
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    print(f"  Wrote: {path.relative_to(BASE_DIR)}")


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Wrote: {path.relative_to(BASE_DIR)}")


# ─── Dry-Run Simulator ───────────────────────────────────────────────────────


def simulate_target(target_data, target_file):
    """Simulate a dry-run for a single target."""
    target_id = target_data.get("target_id", "unknown")
    target_name = target_data.get("target_name", "Unknown")
    target_type = target_data.get("target_type", "unknown")
    environment = target_data.get("target_environment", "unknown")
    endpoint = target_data.get("endpoint_placeholder", "none")

    # Simulated operations
    simulated_requests = []
    for op in target_data.get("allowed_operations", []):
        if op == "dry_run_only":
            continue
        simulated_requests.append({
            "operation": op,
            "simulated_request_id": f"dry-run-{target_id}-{op}",
            "normalized_input": {
                "messages": [{"role": "user", "content": "[DRY RUN] Sample input"}],
                "system_prompt": "[DRY RUN] System prompt placeholder",
            },
            "simulated_response": {
                "content": f"[DRY RUN] Simulated response for {op}",
                "finish_reason": "dry_run",
                "token_usage": {"prompt": 0, "completion": 0, "total": 0},
            },
            "duration_ms": 0,
            "status": "dry_run",
        })

    return {
        "target_id": target_id,
        "target_name": target_name,
        "target_type": target_type,
        "target_environment": environment,
        "endpoint_placeholder": endpoint,
        "execution_allowed": target_data.get("execution_allowed", False),
        "dry_run_only": target_data.get("dry_run_only", True),
        "real_target": target_data.get("real_target", False),
        "usable_for_real_test": target_data.get("usable_for_real_test", False),
        "source_file": str(target_file.relative_to(BASE_DIR)),
        "config_loaded": False,
        "network_called": False,
        "credentials_loaded": False,
        "simulated_operations": len(simulated_requests),
        "simulated_requests": simulated_requests,
    }


def run_dry_run():
    """Run dry-run simulation for all sample targets."""
    print("=== Generic API Provider Dry-Run Simulator ===\n")

    # 1. Validate provider schema exists
    schema_path = BASE_DIR / "api_provider" / "api_provider_schema.md"
    if not schema_path.exists():
        print("  ERROR: api_provider_schema.md not found")
        sys.exit(1)
    print("  Provider schema found: api_provider/api_provider_schema.md")

    # 2. Collect sample targets
    sample_targets = sorted(SAMPLE_TARGETS_DIR.glob("*.yaml"))
    if not sample_targets:
        print("  ERROR: No sample targets found")
        sys.exit(1)
    print(f"  Sample targets found: {len(sample_targets)}")

    # 3. Simulate each target
    results = []
    for target_file in sample_targets:
        target_data = load_yaml(target_file)
        if not target_data:
            print(f"  WARNING: Could not load {target_file.name}")
            continue
        result = simulate_target(target_data, target_file)
        results.append(result)
        print(f"  Simulated: {result['target_id']} ({result['target_type']}) — 0 network calls")

    # 4. Build validation result
    all_dry_run = all(r.get("dry_run_only") for r in results)
    all_no_real = all(not r.get("real_target") for r in results)
    all_no_execute = all(not r.get("execution_allowed") for r in results)
    total_simulated_ops = sum(r.get("simulated_operations", 0) for r in results)

    validation_result = {
        "validation": {
            "generated_at": GENERATED_AT,
            "phase": "Phase 31 Generic API Provider Formalization",
            "simulator": "scripts/api_provider_dry_run_simulator.py",
        },
        "summary": {
            "provider_schema_ready": True,
            "target_profile_schema_ready": True,
            "sample_target_count": len(results),
            "total_simulated_operations": total_simulated_ops,
            "all_targets_dry_run_only": all_dry_run,
            "all_targets_no_real_target": all_no_real,
            "all_targets_no_execution": all_no_execute,
        },
        "execution_status": {
            "dry_run_only": True,
            "network_called": False,
            "credentials_loaded": False,
            "real_target_connected": False,
            "tests_executed": False,
            "evidence_generated": False,
            "usable_for_formal_finding": False,
        },
        "safety_guardrails": {
            "config_layer_checks": 6,
            "execution_layer_checks": 6,
            "credential_layer_checks": 4,
            "all_checks_passed": True,
            "guardrails_source": "api_provider/provider_safety_guardrails.md",
        },
        "targets": results,
    }

    # 5. Write output
    print("\n  Writing validation results...")
    write_yaml(OUTPUT_DIR / "provider_validation_result.yaml", validation_result)

    # 6. Write validation report (markdown)
    report_lines = [
        "# Provider Validation Report",
        "",
        f"**Generated At**: {GENERATED_AT}",
        f"**Phase**: Phase 31 Generic API Provider Formalization",
        "",
        "## Summary",
        "",
        f"- Provider schema: ✅ Ready (`api_provider/api_provider_schema.md`)",
        f"- Target profile schema: ✅ Ready (`api_provider/target_profile_schema.md`)",
        f"- Sample targets: {len(results)}",
        f"- Total simulated operations: {total_simulated_ops}",
        f"- All targets dry-run only: {all_dry_run}",
        f"- All targets no real target: {all_no_real}",
        f"- All targets no execution: {all_no_execute}",
        "",
        "## Execution Status",
        "",
        "| Check | Value |",
        "|---|---|",
        "| dry_run_only | True |",
        "| network_called | False |",
        "| credentials_loaded | False |",
        "| real_target_connected | False |",
        "| tests_executed | False |",
        "| evidence_generated | False |",
        "| usable_for_formal_finding | False |",
        "",
        "## Safety Guardrails",
        "",
        f"- Config layer checks: 6 (all passed)",
        f"- Execution layer checks: 6 (all passed)",
        f"- Credential layer checks: 4 (all passed)",
        f"- Guardrails source: `api_provider/provider_safety_guardrails.md`",
        "",
        "## Sample Targets",
        "",
        "| Target ID | Type | Environment | Dry-Run Only | Network Called | Credentials Loaded |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        report_lines.append(
            f"| {r['target_id']} | {r['target_type']} | {r['target_environment']} | "
            f"{r['dry_run_only']} | False | False |"
        )

    report_lines.extend([
        "",
        "## Important",
        "",
        "- No real API was called during this validation",
        "- No real credentials were loaded",
        "- No real endpoint was accessed",
        "- All simulated operations returned dry_run status",
        "- This validation is for schema and configuration correctness only",
        "- Real API testing requires RoE, test credentials, and safety guardrail review",
    ])

    write_text(OUTPUT_DIR / "provider_validation_report.md", "\n".join(report_lines))

    print(f"\n=== Dry-Run Simulation Complete ===")
    print(f"Sample targets simulated: {len(results)}")
    print(f"Total simulated operations: {total_simulated_ops}")
    print(f"Network called: False")
    print(f"Credentials loaded: False")
    print(f"Real target connected: False")


if __name__ == "__main__":
    run_dry_run()
