"""
Unit Tests for Canonical Metric Quantification Engine.
Path: tests/test_canonical_metric_quantification_engine.py

Task: Phase-98A-METRIC-001
PRD References:
  - 原 PRD v1.0 §6, §7, §10
  - 攻击者视角 §7, §8
  - PRD v2.0 §3, §10.1-§10.2, §13-§14
  - PRD v3.1 §2.1, §3.3, §4
  - GAP-001 闭环要求
"""

import os
import pytest
import yaml
from pathlib import Path

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


@pytest.fixture
def engine():
    """Returns an instantiated CanonicalMetricQuantificationEngine."""
    return CanonicalMetricQuantificationEngine()


# ============================================================================
# 1. Engine Instantiation & Schema Tests
# ============================================================================

def test_engine_initialization(engine):
    assert engine is not None
    assert isinstance(engine, CanonicalMetricQuantificationEngine)
    assert len(engine.rules) >= 8
    assert engine.safety_boundaries["confirmed_vulnerability"] is False
    assert engine.safety_boundaries["synthetic_only"] is True


def test_standard_enums():
    assert [e.value for e in CapabilityValue] == ["high", "medium", "low"]
    assert [e.value for e in RiskLevel] == ["low", "medium", "high"]
    assert [e.value for e in CanonicalStatus] == ["resolved", "unresolved", "not_applicable"]
    assert [e.value for e in ReviewStatus] == ["draft", "approved", "rejected"]
    assert MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value == "documentation_debt_only"


def test_engine_safety_boundaries_constants():
    assert ENGINE_SAFETY_BOUNDARIES["confirmed_vulnerability"] is False
    assert ENGINE_SAFETY_BOUNDARIES["formal_finding_allowed"] is False
    assert ENGINE_SAFETY_BOUNDARIES["production_safety_claimed"] is False
    assert ENGINE_SAFETY_BOUNDARIES["synthetic_only"] is True
    assert ENGINE_SAFETY_BOUNDARIES["red_team_engine_not_executable"] is True
    assert ENGINE_SAFETY_BOUNDARIES["evidence_mode"] == "synthetic_only"


def test_engine_get_safety_boundaries(engine):
    boundaries = engine.get_safety_boundaries()
    assert isinstance(boundaries, dict)
    assert boundaries["confirmed_vulnerability"] is False
    assert boundaries["synthetic_only"] is True
    # 返回副本，修改不应影响引擎内部状态
    boundaries["synthetic_only"] = False
    assert engine.safety_boundaries["synthetic_only"] is True


def test_forbidden_auto_mapping_rules_catalog():
    assert len(FORBIDDEN_AUTO_MAPPING_RULES) == 8
    ids = [r["id"] for r in FORBIDDEN_AUTO_MAPPING_RULES]
    assert ids == [f"FAM-{i:03d}" for i in range(1, 9)]
    for rule in FORBIDDEN_AUTO_MAPPING_RULES:
        assert "rule" in rule
        assert "description" in rule
        assert rule["name"]


# ============================================================================
# 2. Rule Loading & Validation Tests
# ============================================================================

def test_rules_loaded_from_default_schema(engine):
    assert engine.rules_source_path is not None
    assert "canonical_metric_mapping_rules.yaml" in engine.rules_source_path
    assert len(engine.rules) == 8
    approved = [r for r in engine.rules.values() if r.is_approved()]
    assert len(approved) == 8


def test_module_mode_index_built(engine):
    for i in range(43, 51):
        key = (f"M{i}", "adversarial_validation")
        assert key in engine.module_mode_index
        rule_id = engine.module_mode_index[key]
        assert rule_id in engine.rules


def test_gap_closure_index_built(engine):
    expected_gap_modules = {
        "GAP-001": "M44",
        "GAP-002": "M47",
        "GAP-003": "M45",
        "GAP-004": "M46",
        "GAP-005": "M50",
    }
    assert len(engine.gap_closure_index) == 5
    for gap_id, rule_id in engine.gap_closure_index.items():
        rule = engine.rules[rule_id]
        assert rule.closes_gap == gap_id
        assert rule.module_id == expected_gap_modules[gap_id]


def test_validate_rule_definition_valid(engine):
    valid_rule = {
        "rule_id": "RULE-TEST-001",
        "module_id": "M99",
        "assessment_mode": "adversarial_validation",
        "review_status": "approved",
        "capability_value": "high",
        "risk_level": "low",
    }
    is_valid, errors = engine.validate_rule_definition(valid_rule)
    assert is_valid is True
    assert errors == []


@pytest.mark.parametrize("missing_field", [
    "rule_id", "module_id", "assessment_mode",
    "review_status", "capability_value", "risk_level",
])
def test_validate_rule_definition_missing_fields(engine, missing_field):
    rule_data = {
        "rule_id": "RULE-TEST-001",
        "module_id": "M99",
        "assessment_mode": "adversarial_validation",
        "review_status": "approved",
        "capability_value": "high",
        "risk_level": "low",
    }
    del rule_data[missing_field]
    is_valid, errors = engine.validate_rule_definition(rule_data)
    assert is_valid is False
    assert any(missing_field in e for e in errors)


@pytest.mark.parametrize("field,invalid_value", [
    ("capability_value", "ultra"),
    ("risk_level", "extreme"),
    ("review_status", "pending"),
])
def test_validate_rule_definition_invalid_enums(engine, field, invalid_value):
    rule_data = {
        "rule_id": "RULE-TEST-001",
        "module_id": "M99",
        "assessment_mode": "adversarial_validation",
        "review_status": "approved",
        "capability_value": "high",
        "risk_level": "low",
    }
    rule_data[field] = invalid_value
    is_valid, errors = engine.validate_rule_definition(rule_data)
    assert is_valid is False
    assert any(field in e for e in errors)


def test_load_rules_missing_file_raises():
    eng = CanonicalMetricQuantificationEngine(auto_load_rules=False)
    with pytest.raises(FileNotFoundError):
        eng.load_rules("schemas/__nonexistent_rules__.yaml")


def test_load_rules_invalid_rule_raises(tmp_path):
    eng = CanonicalMetricQuantificationEngine(auto_load_rules=False)
    bad_rules = {
        "approved_rules": [
            {
                "rule_id": "RULE-BAD-001",
                "module_id": "M99",
                "assessment_mode": "adversarial_validation",
                "review_status": "approved",
                "capability_value": "ultra",  # invalid
                "risk_level": "low",
            }
        ]
    }
    bad_path = tmp_path / "bad_rules.yaml"
    bad_path.write_text(yaml.safe_dump(bad_rules), encoding="utf-8")
    with pytest.raises(RuleValidationError):
        eng.load_rules(str(bad_path))


def test_register_and_load_custom_rules(tmp_path):
    eng = CanonicalMetricQuantificationEngine(auto_load_rules=False)
    rules = {
        "approved_rules": [
            {
                "rule_id": "RULE-CUSTOM-001",
                "module_id": "M77",
                "module_name": "Custom Test Module",
                "assessment_mode": "adversarial_validation",
                "review_status": "approved",
                "approved_by": "Test Board",
                "approval_date": "2026-08-18",
                "capability_value": "medium",
                "risk_level": "medium",
                "rationale": "test rule",
                "closes_gap": "GAP-099",
                "prerequisites": [],
                "safety_constraints": {"confirmed_vulnerability": False},
            }
        ]
    }
    rules_path = tmp_path / "custom_rules.yaml"
    rules_path.write_text(yaml.safe_dump(rules), encoding="utf-8")

    count = eng.load_rules(str(rules_path))
    assert count == 1
    assert "RULE-CUSTOM-001" in eng.rules
    assert ("M77", "adversarial_validation") in eng.module_mode_index
    assert "GAP-099" in eng.gap_closure_index
    assert eng.rules_source_path == str(rules_path)


# ============================================================================
# 3. Forbidden Auto-Mapping Defense Tests (FAM-001 ~ FAM-008)
# ============================================================================

def test_fam_001_success_rate_auto_mapping_rejected(engine):
    attempt = {
        "success_rate": 0.95,
        "auto_capability_value": "high",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-001") for v in violations)


def test_fam_001_validator_pass_rate_rejected(engine):
    attempt = {
        "validator_pass_rate": 1.0,
        "auto_capability_value": "high",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-001") for v in violations)


def test_fam_002_signal_count_rejected(engine):
    attempt = {
        "signal_count": 42,
        "auto_capability_value": "high",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-002") for v in violations)


def test_fam_002_raw_signals_count_rejected(engine):
    attempt = {
        "raw_signals_count": 10,
        "auto_risk_level": "high",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-002") for v in violations)


def test_fam_003_breakthrough_false_to_low_risk_rejected(engine):
    attempt = {
        "breakthrough_detected": False,
        "inferred_risk_level": "low",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-003") for v in violations)


def test_fam_004_breakthrough_true_to_high_risk_rejected(engine):
    attempt = {
        "breakthrough_detected": True,
        "inferred_risk_level": "high",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-004") for v in violations)


def test_fam_005_human_review_count_rejected(engine):
    attempt = {
        "human_review_count": 7,
        "inferred_risk_level": "medium",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-005") for v in violations)


def test_fam_006_descriptive_capability_field_rejected(engine):
    attempt = {
        "canonical_capability_value": "simulated_capability_signal",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-006") for v in violations)


def test_fam_006_descriptive_risk_field_rejected(engine):
    attempt = {
        "canonical_risk_level": "low_conceptual_only",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-006") for v in violations)


def test_fam_007_safety_flag_conflation_rejected(engine):
    attempt = {
        "conflate_safety_with_risk": True,
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-007") for v in violations)


def test_fam_008_resolved_claim_without_rule_rejected(engine):
    attempt = {
        "claim_resolved_without_rule": True,
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-008") for v in violations)


def test_strict_mode_raises_forbidden_violation():
    eng = CanonicalMetricQuantificationEngine(strict_mode=True)
    attempt = {
        "success_rate": 0.9,
        "auto_capability_value": "high",
    }
    with pytest.raises(ForbiddenAutoMappingViolation) as exc_info:
        eng.check_forbidden_auto_mapping(attempt)
    assert exc_info.value.rule_id == "FAM-001"
    assert "FAM-001" in str(exc_info.value)


def test_explicit_raise_on_violation_flag(engine):
    attempt = {
        "signal_count": 5,
        "auto_risk_level": "low",
    }
    # raise_on_violation=False 覆盖 strict_mode 默认值
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=False)
    assert any(v.startswith("FAM-002") for v in violations)

    non_strict = CanonicalMetricQuantificationEngine(strict_mode=False)
    with pytest.raises(ForbiddenAutoMappingViolation):
        non_strict.check_forbidden_auto_mapping(attempt, raise_on_violation=True)


def test_clean_attempt_data_no_violations(engine):
    attempt = {
        "module_id": "M44",
        "assessment_mode": "adversarial_validation",
        "notes": "常规执行数据，无自动映射尝试",
    }
    violations = engine.check_forbidden_auto_mapping(attempt, raise_on_violation=True)
    assert violations == []


# ============================================================================
# 4. Module Evaluation Tests (M43-M50)
# ============================================================================

@pytest.mark.parametrize("module_id,expected_capability,expected_risk,expected_gap", [
    ("M43", "high", "high", None),
    ("M44", "high", "low", "GAP-001"),
    ("M45", "medium", "medium", "GAP-003"),
    ("M46", "high", "high", "GAP-004"),
    ("M47", "high", "high", "GAP-002"),
    ("M48", "high", "high", None),
    ("M49", "high", "medium", None),
    ("M50", "high", "high", "GAP-005"),
])
def test_evaluate_module_m43_to_m50(engine, module_id, expected_capability, expected_risk, expected_gap):
    result = engine.evaluate_module(module_id, "adversarial_validation")
    assert isinstance(result, CanonicalEvaluationResult)
    assert result.canonical_capability_value == expected_capability
    assert result.canonical_risk_level == expected_risk
    assert result.canonical_capability_status == "resolved"
    assert result.canonical_risk_status == "resolved"
    assert result.mapping_rule_id == f"RULE-{module_id}-CANONICAL-001"
    assert result.mapping_rule_review_status == "approved"
    assert result.future_canonical_metric_normalization_blocked is False
    assert result.gap_closure_id == expected_gap
    assert result.is_resolved() is True
    assert result.unresolved_reason is None
    assert result.rationale


def test_evaluate_module_case_insensitive(engine):
    result = engine.evaluate_module("m44", "ADVERSARIAL_VALIDATION")
    assert result.module_id == "M44"
    assert result.assessment_mode == "adversarial_validation"
    assert result.is_resolved() is True


def test_evaluate_unknown_module_unresolved(engine):
    result = engine.evaluate_module("M99", "adversarial_validation")
    assert result.canonical_capability_status == "unresolved"
    assert result.canonical_risk_status == "unresolved"
    assert result.canonical_capability_value is None
    assert result.canonical_risk_level is None
    assert result.future_canonical_metric_normalization_blocked is True
    assert result.mapping_absence_effect == "documentation_debt_only"
    assert result.unresolved_reason is not None
    assert result.is_resolved() is False


def test_evaluate_wrong_mode_unresolved(engine):
    result = engine.evaluate_module("M44", "defensive_evaluation")
    assert result.canonical_capability_status == "unresolved"
    assert result.future_canonical_metric_normalization_blocked is True
    assert result.is_resolved() is False


def test_draft_rule_cannot_resolve():
    eng = CanonicalMetricQuantificationEngine(auto_load_rules=False)
    draft_rule = MappingRule(
        rule_id="RULE-DRAFT-001",
        module_id="M88",
        module_name="Draft Test Module",
        assessment_mode="adversarial_validation",
        review_status="draft",
        approved_by="Test Board",
        approval_date="2026-08-18",
        capability_value="high",
        risk_level="medium",
        rationale="draft rule for testing",
    )
    eng.register_rule(draft_rule)

    result = eng.evaluate_module("M88", "adversarial_validation")
    assert result.canonical_capability_status == "unresolved"
    assert result.canonical_capability_value is None
    assert result.mapping_rule_review_status == "draft"
    assert result.future_canonical_metric_normalization_blocked is True
    assert result.unresolved_reason is not None
    assert any("draft" in v for v in result.violations_detected)
    assert result.is_resolved() is False


def test_evaluate_module_with_forbidden_execution_data(engine):
    exec_data = {
        "success_rate": 0.99,
        "auto_capability_value": "high",
    }
    result = engine.evaluate_module("M44", "adversarial_validation", execution_data=exec_data)
    # 违规被记录，但规则决议不受非法输入影响（规则推导仅依据已审核规则）
    assert any(v.startswith("FAM-001") for v in result.violations_detected)
    assert result.canonical_capability_value == "high"
    assert result.canonical_risk_level == "low"


def test_descriptive_fields_preserved(engine):
    result = engine.evaluate_module("M44", "adversarial_validation")
    assert result.descriptive_fields["capability_signal_class"] == "simulated_capability_signal"
    assert result.descriptive_fields["risk_qualifier"] == "low_conceptual_only"

    custom = engine.evaluate_module(
        "M44", "adversarial_validation",
        execution_data={"capability_signal_class": "custom_class", "risk_qualifier": "custom_qualifier"},
    )
    assert custom.descriptive_fields["capability_signal_class"] == "custom_class"
    assert custom.descriptive_fields["risk_qualifier"] == "custom_qualifier"


def test_result_safety_fields(engine):
    result = engine.evaluate_module("M44", "adversarial_validation")
    assert result.safety_fields["confirmed_vulnerability"] is False
    assert result.safety_fields["synthetic_only"] is True
    assert result.safety_fields["formal_finding_allowed"] is False


def test_result_to_dict(engine):
    result = engine.evaluate_module("M44", "adversarial_validation")
    d = result.to_dict()
    assert d["module_id"] == "M44"
    assert d["canonical_risk_level"] == "low"
    assert d["mapping_rule_id"] == "RULE-M44-CANONICAL-001"


# ============================================================================
# 5. Batch Evaluation Tests
# ============================================================================

def test_evaluate_batch_default_modules(engine):
    batch = engine.evaluate_batch()
    assert isinstance(batch, BatchCanonicalEvaluationResult)
    assert len(batch.evaluations) == 8
    for i in range(43, 51):
        assert f"M{i}" in batch.evaluations
        assert batch.evaluations[f"M{i}"].is_resolved() is True


def test_evaluate_batch_summary(engine):
    batch = engine.evaluate_batch()
    summary = batch.summary
    assert summary["total_evaluated"] == 8
    assert summary["resolved_count"] == 8
    assert summary["unresolved_count"] == 0
    assert summary["blocked_count"] == 0
    assert summary["approved_rules_in_catalog"] == 8
    assert summary["evidence_mode"] == "synthetic_only"
    assert summary["confirmed_vulnerability"] is False
    assert summary["formal_finding_allowed"] is False
    assert summary["production_safety_claimed"] is False


def test_evaluate_batch_custom_specs(engine):
    specs = [
        {"module_id": "M44", "assessment_mode": "adversarial_validation"},
        {"module_id": "M99", "assessment_mode": "adversarial_validation"},
    ]
    batch = engine.evaluate_batch(specs)
    assert batch.summary["total_evaluated"] == 2
    assert batch.summary["resolved_count"] == 1
    assert batch.summary["unresolved_count"] == 1
    assert batch.summary["blocked_count"] == 1
    assert batch.evaluations["M44"].is_resolved() is True
    assert batch.evaluations["M99"].is_resolved() is False


def test_batch_to_dict(engine):
    batch = engine.evaluate_batch()
    d = batch.to_dict()
    assert "evaluations" in d
    assert "summary" in d
    assert len(d["evaluations"]) == 8


# ============================================================================
# 6. GAP Closure Tests (GAP-001 ~ GAP-005)
# ============================================================================

@pytest.mark.parametrize("gap_id,expected_module", [
    ("GAP-001", "M44"),
    ("GAP-002", "M47"),
    ("GAP-003", "M45"),
    ("GAP-004", "M46"),
    ("GAP-005", "M50"),
])
def test_resolve_gap_closed(engine, gap_id, expected_module):
    result = engine.resolve_gap(gap_id)
    assert result["gap_id"] == gap_id
    assert result["closure_status"] == "closed"
    assert result["target_module"] == expected_module
    assert result["resolving_rule_id"] == f"RULE-{expected_module}-CANONICAL-001"
    assert result["review_status"] == "approved"
    assert result["canonical_capability_value"] is not None
    assert result["canonical_risk_level"] is not None
    assert result["confirmed_vulnerability"] is False


def test_resolve_unknown_gap_unresolved(engine):
    result = engine.resolve_gap("GAP-999")
    assert result["closure_status"] == "unresolved"
    assert "reason" in result
    assert result["confirmed_vulnerability"] is False
    assert result["synthetic_only"] is True


def test_gap_closure_formal_proof_structure(engine):
    result = engine.resolve_gap("GAP-001")
    required_keys = {
        "gap_id", "target_module", "module_name", "closure_status",
        "resolving_rule_id", "review_status", "approved_by", "approval_date",
        "canonical_capability_value", "canonical_risk_level",
    }
    assert required_keys.issubset(result.keys())


# ============================================================================
# 7. Unresolved -> Resolved Transition Tests
# ============================================================================

def test_transition_unresolved_to_resolved_m44(engine):
    transition = engine.simulate_unresolved_to_resolved_transition("M44", "adversarial_validation")
    assert isinstance(transition, TransitionResult)
    assert transition.module_id == "M44"
    assert transition.previous_capability_status == "unresolved"
    assert transition.previous_risk_status == "unresolved"
    assert transition.new_capability_status == "resolved"
    assert transition.new_risk_status == "resolved"
    assert transition.rule_id == "RULE-M44-CANONICAL-001"
    assert transition.gap_closed == "GAP-001"
    assert transition.transition_success is True
    assert transition.non_retroactive_verified is True


def test_transition_fails_without_rule(engine):
    transition = engine.simulate_unresolved_to_resolved_transition("M99", "adversarial_validation")
    assert transition.transition_success is False
    assert transition.new_capability_status == "unresolved"
    assert transition.rule_id == "NONE"


def test_transition_all_m43_to_m50(engine):
    for i in range(43, 51):
        transition = engine.simulate_unresolved_to_resolved_transition(f"M{i}", "adversarial_validation")
        assert transition.transition_success is True
        assert transition.previous_capability_status == "unresolved"
        assert transition.new_capability_status == "resolved"


def test_transition_to_dict(engine):
    transition = engine.simulate_unresolved_to_resolved_transition("M44", "adversarial_validation")
    d = transition.to_dict()
    assert d["module_id"] == "M44"
    assert d["transition_success"] is True
    assert d["non_retroactive_verified"] is True


# ============================================================================
# 8. Scorecard Export Tests
# ============================================================================

def test_export_scorecard_default(engine):
    scorecard = engine.export_scorecard()
    assert scorecard["scorecard_version"] == "1.0"
    assert scorecard["task_id"] == "Phase-98A-METRIC-001"
    assert scorecard["rules_count"] == 8
    assert scorecard["approved_rules_count"] == 8
    assert scorecard["forbidden_auto_mapping_rules_count"] == 8
    assert len(scorecard["module_evaluations"]) == 8
    assert scorecard["batch_summary"]["resolved_count"] == 8


def test_export_scorecard_gap_closures(engine):
    scorecard = engine.export_scorecard()
    gap_closures = scorecard["gap_closures"]
    for gap_id in ("GAP-001", "GAP-002", "GAP-003", "GAP-004", "GAP-005"):
        assert gap_id in gap_closures
        assert gap_closures[gap_id]["closure_status"] == "closed"


def test_export_scorecard_non_retroactive(engine):
    scorecard = engine.export_scorecard()
    nr = scorecard["non_retroactive_declarations"]
    assert nr["retroactive_effect_on_existing_module_closure"] is False
    assert nr["existing_module_conclusions_preserved"] is True
    assert nr["existing_coverage_status_preserved"] is True
    assert nr["existing_scorecard_conclusions_preserved"] is True


def test_export_scorecard_safety_boundaries(engine):
    scorecard = engine.export_scorecard()
    sb = scorecard["safety_boundaries"]
    assert sb["confirmed_vulnerability"] is False
    assert sb["synthetic_only"] is True
    assert sb["formal_finding_allowed"] is False


def test_export_scorecard_custom_modules(engine):
    scorecard = engine.export_scorecard(module_ids=["M44", "M50"])
    assert len(scorecard["module_evaluations"]) == 2
    assert "M44" in scorecard["module_evaluations"]
    assert "M50" in scorecard["module_evaluations"]


# ============================================================================
# 9. Schema File Content Tests
# ============================================================================

def test_schema_file_exists():
    schema_path = Path("schemas/canonical_metric_mapping_rules.yaml")
    assert schema_path.is_file()


def test_schema_non_retroactive_declarations():
    with open("schemas/canonical_metric_mapping_rules.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    nr = data["non_retroactive_declarations"]
    assert nr["retroactive_effect_on_existing_module_closure"] is False
    assert nr["existing_module_conclusions_preserved"] is True


def test_schema_enums_match_engine():
    with open("schemas/canonical_metric_mapping_rules.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    enums = data["canonical_enums"]
    assert enums["capability_value"]["enum"] == [e.value for e in CapabilityValue]
    assert enums["risk_level"]["enum"] == [e.value for e in RiskLevel]
    assert enums["canonical_capability_status"]["enum"] == [e.value for e in CanonicalStatus]
    assert enums["mapping_rule_review_status"]["enum"] == [e.value for e in ReviewStatus]


def test_schema_rules_safety_constraints():
    with open("schemas/canonical_metric_mapping_rules.yaml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    for rule in data["approved_rules"]:
        sc = rule["safety_constraints"]
        assert sc["confirmed_vulnerability"] is False
        assert sc["synthetic_only"] is True
        assert sc["red_team_engine_not_executable"] is True
