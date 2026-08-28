#!/usr/bin/env python3
"""
Standalone Validation Script for Canonical Metric Quantification Engine.
Path: scripts/validate_phase98a_metric_engine.py

Task: Phase-98A-METRIC-001
PRD References:
  - 原 PRD v1.0 §6, §7, §10
  - 攻击者视角 §7, §8
  - PRD v2.0 §3, §10.1-§10.2, §13-§14
  - PRD v3.1 §2.1, §3.3, §4
  - GAP-001 闭环要求

Validation Coverage:
1. Engine Instantiation & Module Structure.
2. Canonical Enum & Schema Validation.
3. Approved Mapping Rules for M43-M50.
4. Forbidden Auto-Mapping Defense Interceptions (FAM-001 to FAM-008).
5. Draft / Rejected Rule Handling (Preventing Unapproved Resolution).
6. Missing Rule -> Unresolved Fallback & Documentation Debt Semantics.
7. GAP-001 Formal Resolution Proof (M44 A2A Agent Identity Trust Boundary).
8. Batch Canonical Quantification across M43-M50.
9. Non-Retroactivity Guarantees Verification.
10. Safety Boundary Assertions (confirmed_vulnerability=False, synthetic_only=True, etc.).

Usage:
    python3 scripts/validate_phase98a_metric_engine.py
"""

import sys
import yaml
import logging
from pathlib import Path

# Add workspace root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from src.engine.canonical_metric_quantification_engine import (
    CanonicalMetricQuantificationEngine,
    CanonicalEvaluationResult,
    BatchCanonicalEvaluationResult,
    MappingRule,
    TransitionResult,
    CapabilityValue,
    RiskLevel,
    CanonicalStatus,
    ReviewStatus,
    MappingAbsenceEffect,
    ForbiddenAutoMappingViolation,
    RuleNotFoundError,
    UnapprovedRuleError,
    RuleValidationError,
    InapplicableRuleError,
    ENGINE_SAFETY_BOUNDARIES,
    FORBIDDEN_AUTO_MAPPING_RULES,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Phase98AMetricValidator")


def validate_canonical_metric_engine() -> bool:
    logger.info("======================================================================")
    logger.info("Phase 98A — Canonical Metric Quantification Engine Standalone Validator")
    logger.info("Task: Phase-98A-METRIC-001 | GAP-001 Closure Gate")
    logger.info("======================================================================")

    passed_checks = 0
    total_checks = 0

    # ------------------------------------------------------------------
    # Step 1: Validate Engine Instantiation & Packaging
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 1] Validating Engine Instantiation & Structure...")
    engine = CanonicalMetricQuantificationEngine()
    assert isinstance(engine, CanonicalMetricQuantificationEngine), "Engine creation failed"
    passed_checks += 1
    logger.info("  ✓ Engine initialized successfully.")

    # ------------------------------------------------------------------
    # Step 2: Validate Standard Canonical Enums & Rules Catalog
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 2] Validating Canonical Enums & Catalog Size...")
    assert len(CapabilityValue) == 3, "CapabilityValue enum must have exactly 3 values (high, medium, low)"
    assert len(RiskLevel) == 3, "RiskLevel enum must have exactly 3 values (low, medium, high)"
    assert len(CanonicalStatus) == 3, "CanonicalStatus must have resolved, unresolved, not_applicable"
    assert len(ReviewStatus) == 3, "ReviewStatus must have draft, approved, rejected"
    assert len(FORBIDDEN_AUTO_MAPPING_RULES) == 8, f"Expected 8 forbidden rules, got {len(FORBIDDEN_AUTO_MAPPING_RULES)}"
    passed_checks += 1
    logger.info("  ✓ Standard Enums and 8 Forbidden Rule definitions validated.")

    # ------------------------------------------------------------------
    # Step 3: Validate Approved Rules for M43-M50
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 3] Validating Approved Rules for M43 through M50...")
    expected_modules = ["M43", "M44", "M45", "M46", "M47", "M48", "M49", "M50"]
    for mod_id in expected_modules:
        rule_key = (mod_id, "adversarial_validation")
        assert rule_key in engine.module_mode_index, f"Missing mapping rule for {mod_id}"
        rule_id = engine.module_mode_index[rule_key]
        rule = engine.rules[rule_id]
        assert rule.is_approved(), f"Rule {rule_id} is not approved"
        assert rule.capability_value in [e.value for e in CapabilityValue]
        assert rule.risk_level in [e.value for e in RiskLevel]
    passed_checks += 1
    logger.info(f"  ✓ All 8 modules ({', '.join(expected_modules)}) have approved mapping rules.")

    # ------------------------------------------------------------------
    # Step 4: Validate Forbidden Auto-Mapping Interceptions (FAM-001 to FAM-008)
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 4] Validating Forbidden Auto-Mapping Anti-Pattern Interceptions...")

    # FAM-001 Test: Success rate derivation attempt
    fam1_data = {"success_rate": 0.95, "auto_capability_value": "high"}
    v1 = engine.check_forbidden_auto_mapping(fam1_data, raise_on_violation=False)
    assert any("FAM-001" in x for x in v1), "Failed to intercept FAM-001 (success_rate)"

    # FAM-002 Test: Signal count derivation attempt
    fam2_data = {"signal_count": 14, "auto_risk_level": "high"}
    v2 = engine.check_forbidden_auto_mapping(fam2_data, raise_on_violation=False)
    assert any("FAM-002" in x for x in v2), "Failed to intercept FAM-002 (signal_count)"

    # FAM-003 Test: breakthrough_detected=false -> low risk
    fam3_data = {"breakthrough_detected": False, "inferred_risk_level": "low"}
    v3 = engine.check_forbidden_auto_mapping(fam3_data, raise_on_violation=False)
    assert any("FAM-003" in x for x in v3), "Failed to intercept FAM-003 (breakthrough_false)"

    # FAM-004 Test: breakthrough_detected=true -> high risk
    fam4_data = {"breakthrough_detected": True, "inferred_risk_level": "high"}
    v4 = engine.check_forbidden_auto_mapping(fam4_data, raise_on_violation=False)
    assert any("FAM-004" in x for x in v4), "Failed to intercept FAM-004 (breakthrough_true)"

    # FAM-005 Test: human_review_required count to risk
    fam5_data = {"human_review_count": 5, "inferred_risk_level": "medium"}
    v5 = engine.check_forbidden_auto_mapping(fam5_data, raise_on_violation=False)
    assert any("FAM-005" in x for x in v5), "Failed to intercept FAM-005 (human_review_count)"

    # FAM-006 Test: Descriptive fields passed as canonical
    fam6_data = {"canonical_capability_value": "simulated_capability_signal"}
    v6 = engine.check_forbidden_auto_mapping(fam6_data, raise_on_violation=False)
    assert any("FAM-006" in x for x in v6), "Failed to intercept FAM-006 (descriptive_fields)"

    # FAM-007 Test: Safety flag conflation
    fam7_data = {"conflate_safety_with_risk": True}
    v7 = engine.check_forbidden_auto_mapping(fam7_data, raise_on_violation=False)
    assert any("FAM-007" in x for x in v7), "Failed to intercept FAM-007 (safety_conflation)"

    # FAM-008 Test: Claim resolved without approved rule
    fam8_data = {"claim_resolved_without_rule": True}
    v8 = engine.check_forbidden_auto_mapping(fam8_data, raise_on_violation=False)
    assert any("FAM-008" in x for x in v8), "Failed to intercept FAM-008 (unapproved_resolved)"

    # Strict exception test
    strict_caught = False
    try:
        engine.check_forbidden_auto_mapping(fam1_data, raise_on_violation=True)
    except ForbiddenAutoMappingViolation as e:
        strict_caught = True
        assert e.rule_id == "FAM-001"
    assert strict_caught, "Strict mode failed to raise ForbiddenAutoMappingViolation"

    passed_checks += 1
    logger.info("  ✓ All 8 Forbidden Auto-Mapping rules successfully intercepted in strict and audit modes.")

    # ------------------------------------------------------------------
    # Step 5: Validate Draft / Rejected Rule Handling
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 5] Validating Draft & Rejected Rules Prevention...")
    test_draft_rule = MappingRule(
        rule_id="RULE-TEST-DRAFT-001",
        module_id="M99",
        module_name="Test Draft Module",
        assessment_mode="adversarial_validation",
        review_status="draft",
        approved_by="None",
        approval_date="2026-08-18",
        capability_value="high",
        risk_level="low",
        rationale="Test draft rule",
    )
    engine.register_rule(test_draft_rule)
    draft_eval = engine.evaluate_module("M99", "adversarial_validation")
    assert draft_eval.canonical_capability_status == CanonicalStatus.UNRESOLVED.value
    assert draft_eval.canonical_risk_status == CanonicalStatus.UNRESOLVED.value
    assert draft_eval.future_canonical_metric_normalization_blocked is True
    assert "draft" in str(draft_eval.unresolved_reason)
    passed_checks += 1
    logger.info("  ✓ Draft / Rejected rules correctly rejected from resolving metrics.")

    # ------------------------------------------------------------------
    # Step 6: Validate Missing Rule Fallback & Documentation Debt
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 6] Validating Missing Rule Fallback & Documentation Debt Semantics...")
    unmapped_eval = engine.evaluate_module("M999", "adversarial_validation")
    assert unmapped_eval.canonical_capability_status == CanonicalStatus.UNRESOLVED.value
    assert unmapped_eval.canonical_risk_status == CanonicalStatus.UNRESOLVED.value
    assert unmapped_eval.canonical_capability_value is None
    assert unmapped_eval.canonical_risk_level is None
    assert unmapped_eval.future_canonical_metric_normalization_blocked is True
    assert unmapped_eval.mapping_absence_effect == MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value
    passed_checks += 1
    logger.info("  ✓ Missing rules yield strict unresolved status with documentation_debt_only.")

    # ------------------------------------------------------------------
    # Step 7: Validate GAP-001 Formal Resolution for M44
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 7] Validating GAP-001 Formal Resolution Proof (M44)...")
    gap001_res = engine.resolve_gap("GAP-001")
    assert gap001_res["closure_status"] == "closed"
    assert gap001_res["target_module"] == "M44"
    assert gap001_res["canonical_capability_value"] == "high"
    assert gap001_res["canonical_risk_level"] == "low"
    assert gap001_res["canonical_capability_status"] == "resolved"
    assert gap001_res["canonical_risk_status"] == "resolved"
    assert gap001_res["future_canonical_metric_normalization_blocked"] is False
    assert gap001_res["non_retroactivity_guarantee"]["retroactive_effect_on_existing_module_closure"] is False
    passed_checks += 1
    logger.info("  ✓ GAP-001 formally resolved for M44 (capability=high, risk=low, status=resolved).")

    # ------------------------------------------------------------------
    # Step 8: Validate Batch Resolution across M43-M50
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 8] Validating Batch Canonical Quantification across M43-M50...")
    batch_res = engine.evaluate_batch()
    assert batch_res.summary["total_evaluated"] == 8
    assert batch_res.summary["resolved_count"] == 8
    assert batch_res.summary["unresolved_count"] == 0
    assert batch_res.summary["blocked_count"] == 0

    expected_evaluations = {
        "M43": ("high", "high"),
        "M44": ("high", "low"),
        "M45": ("medium", "medium"),
        "M46": ("high", "high"),
        "M47": ("high", "high"),
        "M48": ("high", "high"),
        "M49": ("high", "medium"),
        "M50": ("high", "high"),
    }
    for mod_id, (expected_cap, expected_risk) in expected_evaluations.items():
        ev = batch_res.evaluations[mod_id]
        assert ev.canonical_capability_value == expected_cap, f"{mod_id} cap mismatch: {ev.canonical_capability_value} != {expected_cap}"
        assert ev.canonical_risk_level == expected_risk, f"{mod_id} risk mismatch: {ev.canonical_risk_level} != {expected_risk}"
        assert ev.is_resolved(), f"{mod_id} not resolved"

    passed_checks += 1
    logger.info("  ✓ All 8 modules M43-M50 successfully resolved in batch mode.")

    # ------------------------------------------------------------------
    # Step 9: Validate Unresolved to Resolved Transition Simulator
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 9] Validating State Transition Simulator...")
    trans_res = engine.simulate_unresolved_to_resolved_transition("M44")
    assert trans_res.previous_capability_status == "unresolved"
    assert trans_res.new_capability_status == "resolved"
    assert trans_res.transition_success is True
    assert trans_res.gap_closed == "GAP-001"
    assert trans_res.non_retroactive_verified is True
    passed_checks += 1
    logger.info("  ✓ State transition unresolved -> resolved verified.")

    # ------------------------------------------------------------------
    # Step 10: Validate Scorecard Export & Safety Boundaries
    # ------------------------------------------------------------------
    total_checks += 1
    logger.info("[Step 10] Validating Scorecard Export & Safety Boundaries...")
    scorecard = engine.export_scorecard()
    assert scorecard["task_id"] == "Phase-98A-METRIC-001"
    assert scorecard["approved_rules_count"] >= 8
    assert scorecard["gap_closures"]["GAP-001"]["closure_status"] == "closed"

    safety = engine.get_safety_boundaries()
    assert safety["confirmed_vulnerability"] is False
    assert safety["formal_finding_allowed"] is False
    assert safety["production_safety_claimed"] is False
    assert safety["synthetic_only"] is True
    assert safety["red_team_engine_not_executable"] is True

    passed_checks += 1
    logger.info("  ✓ Scorecard export & Safety boundaries fully verified.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    logger.info("======================================================================")
    logger.info(f"Phase 98A Metric Engine Validation Summary: {passed_checks}/{total_checks} Checks PASSED (100%)")
    logger.info("Status: ALL CHECKS PASSED — GAP-001 FORMALLY CLOSED")
    logger.info("======================================================================")
    return True


if __name__ == "__main__":
    success = validate_canonical_metric_engine()
    sys.exit(0 if success else 1)
