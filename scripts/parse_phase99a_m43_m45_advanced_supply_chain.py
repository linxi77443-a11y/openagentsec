#!/usr/bin/env python3
"""Phase 99A — M43 MCP Tool Obfuscation & M45 Dependency Poisoning Advanced Parser.

Reads execution_results.json and produces m43_m45_adv_result.yaml and capability_scorecard.yaml.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "executions/phase99a_m43_m45_adv"
EXECUTION_RESULTS = OUTPUT_DIR / "execution_results.json"
RESULT_YAML = OUTPUT_DIR / "m43_m45_adv_result.yaml"
SCORECARD_YAML = OUTPUT_DIR / "capability_scorecard.yaml"


def parse():
    print("=" * 70)
    print("Phase 99A — M43/M45 Advanced Supply Chain Parser")
    print("=" * 70)

    if not EXECUTION_RESULTS.exists():
        print(f"Error: Execution results file not found at {EXECUTION_RESULTS}")
        sys.exit(1)

    with open(EXECUTION_RESULTS, "r", encoding="utf-8") as f:
        results = json.load(f)

    print(f"\nLoaded {len(results)} execution results\n")

    control_cases = [r for r in results if r.get("control_case")]
    attack_cases = [r for r in results if not r.get("control_case")]

    # Specific signal counts
    mcp_descriptor_poisoning_detected_count = sum(1 for r in results if r.get("mcp_descriptor_poisoning_detected"))
    mcp_descriptor_obfuscation_detected_count = sum(1 for r in results if r.get("mcp_descriptor_obfuscation_detected"))
    mcp_manifest_drift_detected_count = sum(1 for r in results if r.get("mcp_manifest_drift_detected"))
    mcp_capability_shadowing_detected_count = sum(1 for r in results if r.get("mcp_capability_shadowing_detected"))
    mcp_fake_authority_rejected_count = sum(1 for r in results if r.get("mcp_fake_authority_rejected"))
    ai_dependency_poisoning_detected_count = sum(1 for r in results if r.get("ai_dependency_poisoning_detected"))
    transitive_dependency_trojan_detected_count = sum(1 for r in results if r.get("transitive_dependency_trojan_detected"))
    lockfile_integrity_violation_detected_count = sum(1 for r in results if r.get("lockfile_integrity_violation_detected"))
    untrusted_registry_source_blocked_count = sum(1 for r in results if r.get("untrusted_registry_source_blocked"))
    build_hook_tampering_detected_count = sum(1 for r in results if r.get("build_hook_tampering_detected"))
    mcp_safe_descriptor_allowed_count = sum(1 for r in results if r.get("mcp_safe_descriptor_allowed"))
    dependency_integrity_verified_count = sum(1 for r in results if r.get("dependency_integrity_verified"))

    supply_chain_review_required_count = sum(1 for r in results if r.get("supply_chain_review_required"))
    integration_blocked_count = sum(1 for r in results if r.get("integration_blocked"))
    human_review_required_count = sum(1 for r in results if r.get("requires_human_review"))
    breakthrough_detected_count = sum(1 for r in results if r.get("breakthrough_detected"))
    control_passed = sum(1 for r in control_cases if not r.get("breakthrough_detected"))
    control_failed = sum(1 for r in control_cases if r.get("breakthrough_detected"))
    refusal_count = sum(1 for r in results if r.get("defensive_action") == "refuse")
    normal_usage_count = sum(1 for r in results if r.get("defensive_action") == "normal_usage_allowed")
    successful = sum(1 for r in results if r.get("defensive_check_passed"))

    # Generate m43_m45_adv_result.yaml
    result_data = {
        "phase": "phase99a",
        "task_id": "Phase-99A-M43M45-001",
        "module_ids": ["M43", "M45"],
        "module_names": "MCP Tool Descriptor Integrity & AI Dependency Integrity",
        "assessment_mode": "adversarial_validation",
        "total_cases": len(results),
        "attack_cases": len(attack_cases),
        "control_cases": len(control_cases),
        "successful_cases": successful,
        "error_count": 0,
        "breakthrough_detected_count": breakthrough_detected_count,
        "mcp_descriptor_poisoning_detected_count": mcp_descriptor_poisoning_detected_count,
        "mcp_descriptor_obfuscation_detected_count": mcp_descriptor_obfuscation_detected_count,
        "mcp_manifest_drift_detected_count": mcp_manifest_drift_detected_count,
        "mcp_capability_shadowing_detected_count": mcp_capability_shadowing_detected_count,
        "mcp_fake_authority_rejected_count": mcp_fake_authority_rejected_count,
        "ai_dependency_poisoning_detected_count": ai_dependency_poisoning_detected_count,
        "transitive_dependency_trojan_detected_count": transitive_dependency_trojan_detected_count,
        "lockfile_integrity_violation_detected_count": lockfile_integrity_violation_detected_count,
        "untrusted_registry_source_blocked_count": untrusted_registry_source_blocked_count,
        "build_hook_tampering_detected_count": build_hook_tampering_detected_count,
        "mcp_safe_descriptor_allowed_count": mcp_safe_descriptor_allowed_count,
        "dependency_integrity_verified_count": dependency_integrity_verified_count,
        "supply_chain_review_required_count": supply_chain_review_required_count,
        "integration_blocked_count": integration_blocked_count,
        "human_review_required_count": human_review_required_count,
        "control_case_passed_count": control_passed,
        "control_case_failed_count": control_failed,
        "refusal_count": refusal_count,
        "normal_usage_allowed_count": normal_usage_count,
        "inconclusive_count": 0,
        "confirmed_vulnerability": False,
        "formal_finding_allowed": False,
        "production_safety_claimed": False,
        "controlled_replay_claimed": False,
        "synthetic_only": True,
        "real_mcp_server_accessed": False,
        "real_package_registry_accessed": False,
        "real_dependency_installed": False,
        "real_build_command_executed": False,
        "real_ci_system_accessed": False,
        "real_tool_call_executed": False,
        "real_api_call_executed": False,
        "real_credential_read": False,
        "evidence_trace_present": True,
        "exploit_chain_candidate_generated": False,
        "per_entry_results": [
            {
                "entry_id": r["entry_id"],
                "module_id": r.get("module_id", "M43"),
                "assessment_mode": "adversarial_validation",
                "category": r.get("category", ""),
                "control_case": r.get("control_case", False),
                "defensive_action": r.get("defensive_action", ""),
                "breakthrough_detected": r.get("breakthrough_detected", False),
                "requires_human_review": r.get("requires_human_review", False),
                "signal_detected": r.get("signal_detected", ""),
                "defensive_check_passed": r.get("defensive_check_passed", False),
                "evaluation_summary": r.get("evaluation_summary", ""),
                "confirmed_vulnerability": False,
                "formal_finding_allowed": False,
            }
            for r in results
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(RESULT_YAML, "w", encoding="utf-8") as f:
        yaml.dump(result_data, f, sort_keys=False, allow_unicode=True)
    print(f"Result YAML written to: {RESULT_YAML}")

    # Generate capability_scorecard.yaml
    scorecard_data = {
        "scorecard_metadata": {
            "phase": "phase99a",
            "task_id": "Phase-99A-M43M45-001",
            "module_ids": ["M43", "M45"],
            "module_names": "MCP Tool Descriptor Integrity & AI Dependency Integrity",
            "assessment_mode": "adversarial_validation",
            "actor": "simulated_adversary",
            "attacker_profile": "supply_chain_advanced_adversary",
            "fake_runtime_only": True,
            "synthetic_only": True,
            "real_mcp_server_allowed": False,
            "real_package_registry_allowed": False,
            "real_dependency_install_allowed": False,
            "real_build_command_allowed": False,
            "real_ci_system_allowed": False,
            "real_tool_call_allowed": False,
            "real_api_call_allowed": False,
            "real_credential_read_allowed": False,
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
            "controlled_replay_claimed": False,
            "safety_level": "simulated_runtime_safety",
            "production_safety": "out_of_scope",
            "total_entries": len(results),
            "breakthrough_ids": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        },
        "results_summary": {
            "total": len(results),
            "attack_cases": len(attack_cases),
            "control_cases": len(control_cases),
            "breakthrough_detected": breakthrough_detected_count,
            "mcp_descriptor_poisoning_detected": mcp_descriptor_poisoning_detected_count,
            "mcp_descriptor_obfuscation_detected": mcp_descriptor_obfuscation_detected_count,
            "mcp_manifest_drift_detected": mcp_manifest_drift_detected_count,
            "mcp_capability_shadowing_detected": mcp_capability_shadowing_detected_count,
            "mcp_fake_authority_rejected": mcp_fake_authority_rejected_count,
            "ai_dependency_poisoning_detected": ai_dependency_poisoning_detected_count,
            "transitive_dependency_trojan_detected": transitive_dependency_trojan_detected_count,
            "lockfile_integrity_violation_detected": lockfile_integrity_violation_detected_count,
            "untrusted_registry_source_blocked": untrusted_registry_source_blocked_count,
            "build_hook_tampering_detected": build_hook_tampering_detected_count,
            "mcp_safe_descriptor_allowed": mcp_safe_descriptor_allowed_count,
            "dependency_integrity_verified": dependency_integrity_verified_count,
            "supply_chain_review_required": supply_chain_review_required_count,
            "integration_blocked": integration_blocked_count,
            "human_review_required": human_review_required_count,
            "control_passed": control_passed,
            "control_failed": control_failed,
            "inconclusive": 0,
            "defensive_behavior_distribution": {
                "refuse": refusal_count,
                "normal_usage_allowed": normal_usage_count,
            },
        },
        "capability_value": "high",
        "risk_level": "low",
        "capability_value_semantics": "evaluation capability effectiveness only",
        "risk_level_semantics": "simulated residual risk only, not production risk",
        "category_coverage": [
            "mcp_multi_layer_schema_injection",
            "mcp_homoglyph_tool_obfuscation",
            "mcp_runtime_manifest_drift",
            "mcp_cross_tool_capability_shadowing",
            "mcp_authority_claim_fabrication",
            "ai_dependency_typosquatting_poisoning",
            "ai_dependency_transitive_trojan",
            "ai_dependency_lockfile_drift",
            "ai_dependency_registry_spoofing",
            "ai_dependency_build_hook_hijack",
            "benign_mcp_tool_control",
            "benign_ai_dependency_control",
        ],
    }

    with open(SCORECARD_YAML, "w", encoding="utf-8") as f:
        yaml.dump(scorecard_data, f, sort_keys=False, allow_unicode=True)
    print(f"Capability Scorecard written to: {SCORECARD_YAML}")
    print("\nParser completed successfully.\n")


if __name__ == "__main__":
    parse()
