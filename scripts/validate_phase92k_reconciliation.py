#!/usr/bin/env python3
"""Phase-92K Batch Review Reconciliation Validator"""
import os, sys, yaml
DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")
RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
checks = []; P = 0; F = 0
def check(d, c):
    global P, F; checks.append((d,c))
    if c: P += 1; print(f"  ✅ {d}")
    else: F += 1; print(f"  ❌ {d}")

print("\n=== Phase-92K Reconciliation ===")

# V001: 交付物
for f in ["phase92k_batch_review_reconciliation.md","phase92k_coverage_reconciliation_m14_m39.yaml",
          "phase92k_tooltrace_evidence_chain.yaml","phase92k_parser_guard_coverage_proof.yaml",
          "phase92k_knownbad_reconciliation.yaml","phase92k_statreg_reconciliation.yaml",
          "phase92k_shared_asset_declarations.yaml"]:
    check(f"doc: {f}", os.path.exists(os.path.join(DOCS, f)))
check("result yaml", os.path.exists(os.path.join(RESULTS, "phase92k_batch_review_reconciliation_result.yaml")))

# V002: 计数修正
result = yaml.safe_load(open(os.path.join(RESULTS, "phase92k_batch_review_reconciliation_result.yaml")))
check("corrected_count=7", result["count_correction"]["corrected_count"] == 7)
check("7 per_review_status entries", len(result["per_review_status"]) == 7)

# V003: 各审核结论
for phase, data in result["per_review_status"].items():
    check(f"{phase} conclusion=approved", data["conclusion"] == "approved")
    check(f"{phase} pending_judge_reconciliation=true", data.get("pending_judge_reconciliation") is True)

# V004: Coverage reconciliation
cov = yaml.safe_load(open(os.path.join(DOCS, "phase92k_coverage_reconciliation_m14_m39.yaml")))
check("M14 fake_runtime_ready in depth追加", "fake_runtime_ready" in cov["m14_coverage"]["coverage_depth追加"])
check("M39 fake_runtime_ready in depth追加", "fake_runtime_ready" in cov["m39_coverage"]["coverage_depth追加"])
check("M14 safety_level_before=proposal_safety", cov["m14_coverage"]["safety_level_before"] == "proposal_safety")
check("M39 safety_level_before=proposal_safety", cov["m39_coverage"]["safety_level_before"] == "proposal_safety")
check("M14 coverage_credit_granted=false", cov["m14_coverage"]["coverage_credit_granted"] is False)
check("M39 coverage_credit_granted=false", cov["m39_coverage"]["coverage_credit_granted"] is False)

# V005: Tool Trace evidence chain
tt = yaml.safe_load(open(os.path.join(DOCS, "phase92k_tooltrace_evidence_chain.yaml")))
check("TT real_tool_execution_allowed=false", tt.get("real_tool_execution_allowed") is False)
check("TT coverage_credit=0", tt.get("coverage_credit") == 0)
check("TT backward v1.0 pass", tt.get("backward_compatibility", {}).get("v1_0_compatible") is True)
check("TT backward v0.9 rejected", tt.get("backward_compatibility", {}).get("v0_9_rejected") is True)

# V006: Parser guard coverage proof
pg = yaml.safe_load(open(os.path.join(DOCS, "phase92k_parser_guard_coverage_proof.yaml")))
check("PG 11 modules", len(pg["module_coverage"]) == 11)
check("PG detect_functions_unmodified", pg["historical_logic_preserved"]["detect_functions_unmodified"] is True)
check("PG dispatch_functions_unmodified", pg["historical_logic_preserved"]["dispatch_functions_unmodified"] is True)
check("PG coverage_credit=0", pg["coverage_credit"] == 0)

# V007: Known-Bad reconciliation
kb = yaml.safe_load(open(os.path.join(DOCS, "phase92k_knownbad_reconciliation.yaml")))
r = kb["reconciliation"]
check("KB expected_detection=6", r["expected_detection_count"] == 6)
check("KB detected=6", r["detected_count"] == 6)
check("KB missed=0", r["missed_known_bad_count"] == 0)
check("KB false_accept=0", r["false_accept_count"] == 0)
check("KB coverage_credit=0", kb["coverage_credit"] == 0)

# V008: StatReg reconciliation
sr = yaml.safe_load(open(os.path.join(DOCS, "phase92k_statreg_reconciliation.yaml")))
r2 = sr["reconciliation"]
check("SR baseline_version present", r2["baseline_version"] is not None)
check("SR sample_size=5", r2["sample_size"] == 5)
check("SR seed=42", r2["seed"] == 42)
check("SR regression_detected=false", r2["regression_detected"] is False)
check("SR baseline_update_allowed=false", r2["baseline_update_allowed"] is False)
check("SR production_safety_claimed=false", r2["production_safety_claimed"] is False)
check("SR coverage_credit=0", sr["coverage_credit"] == 0)

# V009: SHARED declarations
sa = yaml.safe_load(open(os.path.join(DOCS, "phase92k_shared_asset_declarations.yaml")))
d = sa["declarations"]
check("SHARED assessment_execution_performed=false", d["assessment_execution_performed"] is False)
check("SHARED capability_value_declared=false", d["capability_value_declared"] is False)
check("SHARED risk_level_declared=false", d["risk_level_declared"] is False)
check("SHARED coverage_change_claimed=false", d["coverage_change_claimed"] is False)
check("SHARED registered_module=false", d["registered_module"] is False)

# V010: Safety fields
sf = result["safety_fields"]
check("confirmed_vulnerability=false", sf["confirmed_vulnerability"] is False)
check("formal_finding_allowed=false", sf["formal_finding_allowed"] is False)
check("production_safety_claimed=false", sf["production_safety_claimed"] is False)
check("controlled_replay_execution_allowed=false", sf["controlled_replay_execution_allowed"] is False)
check("attack_execution_allowed=false", sf["attack_execution_allowed"] is False)
check("payload_generation_allowed=false", sf["payload_generation_allowed"] is False)
check("real_target_selection_allowed=false", sf["real_target_selection_allowed"] is False)
check("real_system_connection_allowed=false", sf["real_system_connection_allowed"] is False)
check("real_tool_execution_allowed=false", sf["real_tool_execution_allowed"] is False)
check("real_data_access_allowed=false", sf["real_data_access_allowed"] is False)
check("synthetic_only=true", sf["synthetic_only"] is True)

# V011: No execution
check("no_execution=true", result["no_execution"] is True)

print(f"\n{'='*60}")
print(f"Phase-92K: {P}/{P+F} checks passed")
print(f"{'='*60}")
sys.exit(0 if F == 0 else 1)
