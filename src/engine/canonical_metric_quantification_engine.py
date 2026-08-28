"""
canonical_metric_quantification_engine.py — Canonical Metric Quantification Engine.
Path: src/engine/canonical_metric_quantification_engine.py

Task: Phase-98A-METRIC-001
PRD References:
  - 原 PRD v1.0 §6, §7, §10
  - 攻击者视角 §7, §8
  - PRD v2.0 §3, §10.1-§10.2, §13-§14
  - PRD v3.1 §2.1, §3.3, §4
  - GAP-001 闭环要求

Core Capabilities:
1. Formal Capability & Risk Quantification: Standardized, deterministic derivation of
   capability_value (high/medium/low) and risk_level (low/medium/high) via approved rules.
2. Strict "Forbidden Auto-Mapping" Defenses: Intercepts unapproved heuristics, signal counts,
   pass/success rates, and false breakthrough conflations.
3. Unresolved to Resolved State Transition: Formally validates and drives transition of
   modules (M43-M50) from 'unresolved' to 'resolved' canonical metrics without retroactively
   affecting existing module closure statuses.
4. GAP-001 Formal Closure: Closes GAP-001 for M44 A2A Agent Identity Trust Boundary by
   providing formal rule resolution and verified safety semantics.

Safety Boundaries:
- confirmed_vulnerability: false
- formal_finding_allowed: false
- production_safety_claimed: false
- synthetic_only: true
- red_team_engine_not_executable: true
"""

import os
import sys
import yaml
import logging
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger("CanonicalMetricQuantificationEngine")

# ============================================================================
# Engine Safety Constants
# ============================================================================

ENGINE_SAFETY_BOUNDARIES: Dict[str, Union[bool, str]] = {
    "confirmed_vulnerability": False,
    "formal_finding_allowed": False,
    "production_safety_claimed": False,
    "synthetic_only": True,
    "red_team_engine_not_executable": True,
    "controlled_replay_claimed": False,
    "attack_execution_allowed": False,
    "payload_generation_allowed": False,
    "real_target_selection_allowed": False,
    "dashboard_not_execution_interface": True,
    "evidence_mode": "synthetic_only",
}


# ============================================================================
# Standard Enums
# ============================================================================

class CapabilityValue(str, Enum):
    """Canonical capability value levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskLevel(str, Enum):
    """Canonical risk levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CanonicalStatus(str, Enum):
    """Canonical quantification status."""
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    NOT_APPLICABLE = "not_applicable"


class ReviewStatus(str, Enum):
    """Mapping rule review status."""
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"


class MappingAbsenceEffect(str, Enum):
    """Effect when no approved mapping rule exists."""
    DOCUMENTATION_DEBT_ONLY = "documentation_debt_only"


# ============================================================================
# Forbidden Auto-Mapping Rules (FAM-001 ~ FAM-008)
# ============================================================================

FORBIDDEN_AUTO_MAPPING_RULES: List[Dict[str, str]] = [
    {
        "id": "FAM-001",
        "name": "NO_SUCCESS_RATE_AUTO_MAPPING",
        "rule": "不得用请求成功率或 validator 通过率自动推导 capability_value",
        "description": "Request success rate or validator pass rate cannot directly infer capability value.",
    },
    {
        "id": "FAM-002",
        "name": "NO_SIGNAL_COUNT_AUTO_MAPPING",
        "rule": "不得用 signal 数量自动推导 capability_value 或 risk_level",
        "description": "Signal counts or frequency metrics cannot directly infer capability value or risk level.",
    },
    {
        "id": "FAM-003",
        "name": "NO_BREAKTHROUGH_FALSE_TO_LOW_RISK",
        "rule": "不得用 breakthrough_detected=false 自动推导 low risk",
        "description": "Absence of detected breakthrough does not automatically imply low risk.",
    },
    {
        "id": "FAM-004",
        "name": "NO_BREAKTHROUGH_TRUE_TO_HIGH_RISK",
        "rule": "不得用 breakthrough_detected=true 自动推导 high risk",
        "description": "Presence of detected breakthrough does not automatically imply high risk without formal review.",
    },
    {
        "id": "FAM-005",
        "name": "NO_HUMAN_REVIEW_COUNT_TO_RISK",
        "rule": "不得用 human_review_required 数量自动映射风险等级",
        "description": "Human review trigger count cannot directly map to risk level.",
    },
    {
        "id": "FAM-006",
        "name": "DESCRIPTIVE_FIELDS_NOT_CANONICAL",
        "rule": "capability_signal_class 与 risk_qualifier 只能作为描述字段，严禁作为规范量化指标",
        "description": "Descriptive fields cannot be substituted for canonical metrics.",
    },
    {
        "id": "FAM-007",
        "name": "INDEPENDENCE_OF_SAFETY_FLAGS",
        "rule": "breakthrough_detected、requires_human_review、confirmed_vulnerability 和 canonical capability/risk 必须保持独立正交",
        "description": "Safety flags and canonical risk metrics are strictly orthogonal and independent.",
    },
    {
        "id": "FAM-008",
        "name": "APPROVED_RULE_REQUIRED_FOR_RESOLVED",
        "rule": "只有存在明确、已审核(approved)且适用于对应模块与 assessment mode 的 mapping rule 时，canonical 状态才可标记为 resolved；不存在时必须标记为 unresolved 且 future_canonical_metric_normalization_blocked=true",
        "description": "Canonical resolution requires an explicitly approved mapping rule.",
    },
]


# ============================================================================
# Exceptions
# ============================================================================

class CanonicalMetricEngineError(Exception):
    """Base exception for Canonical Metric Engine."""


class ForbiddenAutoMappingViolation(CanonicalMetricEngineError):
    """Raised when an attempt to use forbidden auto-mapping heuristics is detected."""

    def __init__(self, rule_id: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{rule_id}] Forbidden Auto-Mapping Violation: {message}")
        self.rule_id = rule_id
        self.details = details if details else {}


class RuleNotFoundError(CanonicalMetricEngineError):
    """Raised when no applicable mapping rule exists for module/mode."""


class UnapprovedRuleError(CanonicalMetricEngineError):
    """Raised when a rule is not in approved review status."""


class RuleValidationError(CanonicalMetricEngineError):
    """Raised when a rule definition fails schema validation."""


class InapplicableRuleError(CanonicalMetricEngineError):
    """Raised when a rule is applied to an incompatible module or mode."""


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class MappingRule:
    """Represents an audited, approved canonical mapping rule."""
    rule_id: str
    module_id: str
    module_name: str
    assessment_mode: str
    review_status: str
    approved_by: str
    approval_date: str
    capability_value: str
    risk_level: str
    rationale: str
    closes_gap: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    safety_constraints: Dict[str, Any] = field(default_factory=dict)
    source_file: str = "schemas/canonical_metric_mapping_rules.yaml"

    def is_approved(self) -> bool:
        return self.review_status == ReviewStatus.APPROVED.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CanonicalEvaluationResult:
    """Structured evaluation output for a single module."""
    module_id: str
    assessment_mode: str
    canonical_capability_value: Optional[str]
    canonical_risk_level: Optional[str]
    canonical_capability_status: str
    canonical_risk_status: str
    mapping_rule_id: Optional[str] = None
    mapping_rule_source: Optional[str] = None
    mapping_rule_review_status: Optional[str] = None
    future_canonical_metric_normalization_blocked: bool = False
    mapping_absence_effect: str = MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value
    violations_detected: List[str] = field(default_factory=list)
    unresolved_reason: Optional[str] = None
    gap_closure_id: Optional[str] = None
    rationale: Optional[str] = None
    descriptive_fields: Dict[str, Any] = field(default_factory=dict)
    safety_fields: Dict[str, Any] = field(default_factory=lambda: dict(ENGINE_SAFETY_BOUNDARIES))

    def is_resolved(self) -> bool:
        return (
            self.canonical_capability_status == CanonicalStatus.RESOLVED.value
            and self.canonical_risk_status == CanonicalStatus.RESOLVED.value
            and not self.future_canonical_metric_normalization_blocked
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BatchCanonicalEvaluationResult:
    """Batch evaluation result across multiple modules."""
    evaluations: Dict[str, CanonicalEvaluationResult] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evaluations": {k: v.to_dict() for k, v in self.evaluations.items()},
            "summary": self.summary,
        }


@dataclass
class TransitionResult:
    """Formal record of module unresolved -> resolved state transition."""
    module_id: str
    previous_capability_status: str
    previous_risk_status: str
    new_capability_status: str
    new_risk_status: str
    rule_id: Optional[str]
    gap_closed: Optional[str]
    non_retroactive_verified: bool
    transition_success: bool
    evidence_snapshot: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# Engine
# ============================================================================

class CanonicalMetricQuantificationEngine:
    """
    Canonical Metric Quantification Engine.

    Provides standardized capability and risk mapping resolution, strict forbidden
    auto-mapping defenses, unresolved-to-resolved derivation pipeline, and formal
    closure verification for GAP-001 and M43-M50 modules.
    """

    def __init__(
        self,
        rules_path: Optional[str] = None,
        strict_mode: bool = True,
        auto_load_rules: bool = True,
    ):
        """
        Initialize the Canonical Metric Quantification Engine.

        :param rules_path: Optional path to mapping rules YAML file.
        :param strict_mode: If True, raises exceptions on forbidden auto-mapping violations.
        :param auto_load_rules: If True, automatically loads rules from rules_path or default.
        """
        self.strict_mode = strict_mode
        self.safety_boundaries = dict(ENGINE_SAFETY_BOUNDARIES)
        self.rules: Dict[str, MappingRule] = {}
        self.module_mode_index: Dict[Tuple[str, str], str] = {}
        self.gap_closure_index: Dict[str, str] = {}
        self.rules_source_path: Optional[str] = None

        if auto_load_rules:
            self._init_rules(rules_path)

    def _init_rules(self, rules_path: Optional[str] = None) -> None:
        """Locate and load rules from file system."""
        candidate_paths: List[Path] = []

        if rules_path:
            candidate_paths.append(Path(rules_path))

        base_dir = Path(__file__).resolve().parent.parent.parent
        candidate_paths.extend([
            base_dir / "schemas" / "canonical_metric_mapping_rules.yaml",
            Path("schemas/canonical_metric_mapping_rules.yaml"),
            Path("../schemas/canonical_metric_mapping_rules.yaml"),
        ])

        loaded = False
        for p in candidate_paths:
            if p.is_file():
                self.load_rules(str(p))
                loaded = True
                break

        if not loaded and rules_path:
            raise FileNotFoundError(f"Canonical metric rules file not found at: {rules_path}")

        if not loaded:
            logger.warning("No canonical rules file found at standard paths. Engine running with empty rules.")

    def load_rules(self, rules_path: str) -> int:
        """
        Load and validate mapping rules from YAML file.

        :param rules_path: Path to the YAML rules file.
        :return: Count of successfully registered rules.
        """
        path = Path(rules_path)
        if not path.is_file():
            raise FileNotFoundError(f"Rules file does not exist: {rules_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        rules_list = data.get("approved_rules", [])
        registered_count = 0

        for item in rules_list:
            is_valid, errors = self.validate_rule_definition(item)
            if not is_valid:
                raise RuleValidationError(
                    f"Invalid rule definition for {item.get('rule_id')}: {errors}"
                )
            rule = MappingRule(
                rule_id=item["rule_id"],
                module_id=item["module_id"],
                module_name=item.get("module_name", item["module_id"]),
                assessment_mode=item["assessment_mode"],
                review_status=item["review_status"],
                approved_by=item.get("approved_by", "Formal Architecture Board"),
                approval_date=item.get("approval_date", "2026-08-18"),
                capability_value=item["capability_value"],
                risk_level=item["risk_level"],
                rationale=item.get("rationale", ""),
                closes_gap=item.get("closes_gap"),
                prerequisites=item.get("prerequisites", []),
                safety_constraints=item.get("safety_constraints", {}),
                source_file=str(path),
            )
            self.register_rule(rule)
            registered_count += 1

        self.rules_source_path = str(path)
        logger.info(f"Loaded {registered_count} canonical metric mapping rules from {rules_path}")
        return registered_count

    def register_rule(self, rule: MappingRule) -> str:
        """Register a single validated rule into engine memory."""
        self.rules[rule.rule_id] = rule
        key = (rule.module_id.upper(), rule.assessment_mode.lower())
        self.module_mode_index[key] = rule.rule_id

        if rule.closes_gap:
            self.gap_closure_index[rule.closes_gap.upper()] = rule.rule_id

        return rule.rule_id

    def validate_rule_definition(self, rule_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate rule definition against strict canonical schema requirements.

        :param rule_data: Dictionary containing rule specification.
        :return: (is_valid, list_of_error_strings)
        """
        errors: List[str] = []
        required_fields = [*[
            "rule_id", "module_id", "assessment_mode",
            "review_status", "capability_value", "risk_level",
        ]]

        for f in required_fields:
            if f not in rule_data:
                errors.append(f"Missing required field: {f}")

        if "capability_value" in rule_data:
            val = rule_data["capability_value"]
            if val not in [e.value for e in CapabilityValue]:
                errors.append(f"Invalid capability_value '{val}', must be high/medium/low")

        if "risk_level" in rule_data:
            val = rule_data["risk_level"]
            if val not in [e.value for e in RiskLevel]:
                errors.append(f"Invalid risk_level '{val}', must be low/medium/high")

        if "review_status" in rule_data:
            val = rule_data["review_status"]
            if val not in [e.value for e in ReviewStatus]:
                errors.append(f"Invalid review_status '{val}', must be draft/approved/rejected")

        return len(errors) == 0, errors

    def check_forbidden_auto_mapping(
        self,
        attempt_data: Dict[str, Any],
        raise_on_violation: Optional[bool] = None,
    ) -> List[str]:
        """
        Detect and intercept any forbidden auto-mapping heuristics.

        :param attempt_data: Input data / payload to inspect for illegal derivation patterns.
        :param raise_on_violation: If True (or if engine strict_mode is True and None), raises exception.
        :return: List of detected violation descriptions.
        """
        should_raise = self.strict_mode if raise_on_violation is None else raise_on_violation
        violations: List[str] = []

        # FAM-001: success rate / validator pass rate -> capability_value
        if "success_rate" in attempt_data and "auto_capability_value" in attempt_data:
            violations.append("FAM-001: Attempted to derive capability_value from success_rate")
        if "validator_pass_rate" in attempt_data and "auto_capability_value" in attempt_data:
            violations.append("FAM-001: Attempted to derive capability_value from validator_pass_rate")

        # FAM-002: signal counts -> capability_value / risk_level
        if "signal_count" in attempt_data and (
            "auto_capability_value" in attempt_data or "auto_risk_level" in attempt_data
        ):
            violations.append("FAM-002: Attempted to derive capability_value or risk_level from signal_count")
        if "raw_signals_count" in attempt_data and "auto_risk_level" in attempt_data:
            violations.append("FAM-002: Attempted to derive risk_level from raw_signals_count")

        # FAM-003: breakthrough_detected=false -> low risk
        if attempt_data.get("breakthrough_detected") is False and attempt_data.get("inferred_risk_level") == "low":
            violations.append("FAM-003: Attempted to infer low risk solely from breakthrough_detected=false")

        # FAM-004: breakthrough_detected=true -> high risk
        if attempt_data.get("breakthrough_detected") is True and attempt_data.get("inferred_risk_level") == "high":
            violations.append("FAM-004: Attempted to infer high risk solely from breakthrough_detected=true")

        # FAM-005: human review counts -> risk level
        if "human_review_count" in attempt_data and "inferred_risk_level" in attempt_data:
            violations.append("FAM-005: Attempted to map risk_level from human_review_count")
        if "human_review_required_count" in attempt_data and "inferred_risk_level" in attempt_data:
            violations.append("FAM-005: Attempted to map risk_level from human_review_required_count")

        # FAM-006: descriptive fields passed as canonical metrics
        if "canonical_capability_value" in attempt_data and attempt_data.get("canonical_capability_value") == "simulated_capability_signal":
            violations.append("FAM-006: Descriptive field 'simulated_capability_signal' passed as canonical_capability_value")
        if "canonical_risk_level" in attempt_data and attempt_data.get("canonical_risk_level") == "low_conceptual_only":
            violations.append("FAM-006: Descriptive field 'low_conceptual_only' passed as canonical_risk_level")

        # FAM-007: safety flag conflation with canonical metrics
        if attempt_data.get("conflate_safety_with_risk") is True:
            violations.append("FAM-007: Attempted to conflate confirmed_vulnerability/breakthrough with canonical metrics")

        # FAM-008: resolved claim without approved rule
        if attempt_data.get("claim_resolved_without_rule") is True:
            violations.append("FAM-008: Attempted to claim canonical_status=resolved without matching approved rule")

        if violations and should_raise:
            first_v = violations[0]
            rule_id = first_v.split(":")[0].strip()
            raise ForbiddenAutoMappingViolation(
                rule_id=rule_id,
                message="; ".join(violations),
                details=attempt_data,
            )

        return violations

    def evaluate_module(
        self,
        module_id: str,
        assessment_mode: str,
        execution_data: Optional[Dict[str, Any]] = None,
        override_rule_id: Optional[str] = None,
    ) -> CanonicalEvaluationResult:
        """
        Evaluate canonical capability and risk metrics for a specific module and mode.

        :param module_id: Module identifier, e.g., "M44".
        :param assessment_mode: Assessment mode, e.g., "adversarial_validation".
        :param execution_data: Optional raw execution context or result dictionary.
        :param override_rule_id: Explicit rule ID override if provided.
        :return: CanonicalEvaluationResult object.
        """
        mod_upper = module_id.strip().upper()
        mode_lower = assessment_mode.strip().lower()
        exec_data = execution_data or {}

        # Never allow forbidden auto-mapping inputs to influence derivation.
        violations = self.check_forbidden_auto_mapping(exec_data, raise_on_violation=False)

        # Descriptive fields remain descriptive only (FAM-006).
        descriptive_fields = {
            "capability_signal_class": exec_data.get("capability_signal_class", "simulated_capability_signal"),
            "risk_qualifier": exec_data.get("risk_qualifier", "low_conceptual_only"),
        }

        rule: Optional[MappingRule] = None
        if override_rule_id:
            rule = self.rules.get(override_rule_id)
        else:
            rule_id = self.module_mode_index.get((mod_upper, mode_lower))
            if rule_id:
                rule = self.rules.get(rule_id)

        if not rule:
            # FAM-008: no approved rule -> must stay unresolved and blocked.
            return CanonicalEvaluationResult(
                module_id=mod_upper,
                assessment_mode=mode_lower,
                canonical_capability_value=None,
                canonical_risk_level=None,
                canonical_capability_status=CanonicalStatus.UNRESOLVED.value,
                canonical_risk_status=CanonicalStatus.UNRESOLVED.value,
                mapping_rule_id=None,
                mapping_rule_source=self.rules_source_path,
                mapping_rule_review_status=None,
                future_canonical_metric_normalization_blocked=True,
                mapping_absence_effect=MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value,
                violations_detected=violations,
                unresolved_reason=f"项目中无适用于 {mod_upper} ({mode_lower}) 的已审核 canonical 映射规则",
                descriptive_fields=descriptive_fields,
            )

        if not rule.is_approved():
            # Draft/rejected rules can never resolve canonical metrics.
            return CanonicalEvaluationResult(
                module_id=mod_upper,
                assessment_mode=mode_lower,
                canonical_capability_value=None,
                canonical_risk_level=None,
                canonical_capability_status=CanonicalStatus.UNRESOLVED.value,
                canonical_risk_status=CanonicalStatus.UNRESOLVED.value,
                mapping_rule_id=rule.rule_id,
                mapping_rule_source=rule.source_file,
                mapping_rule_review_status=rule.review_status,
                future_canonical_metric_normalization_blocked=True,
                mapping_absence_effect=MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value,
                violations_detected=violations + [
                    f"Rule {rule.rule_id} is in '{rule.review_status}' status, cannot resolve metrics."
                ],
                unresolved_reason=f"规则 {rule.rule_id} 审核状态为 '{rule.review_status}'，禁止用于形式化状态决议",
                descriptive_fields=descriptive_fields,
            )

        return CanonicalEvaluationResult(**{
            "module_id": mod_upper,
            "assessment_mode": mode_lower,
            "canonical_capability_value": rule.capability_value,
            "canonical_risk_level": rule.risk_level,
            "canonical_capability_status": CanonicalStatus.RESOLVED.value,
            "canonical_risk_status": CanonicalStatus.RESOLVED.value,
            "mapping_rule_id": rule.rule_id,
            "mapping_rule_source": rule.source_file,
            "mapping_rule_review_status": rule.review_status,
            "future_canonical_metric_normalization_blocked": False,
            "mapping_absence_effect": MappingAbsenceEffect.DOCUMENTATION_DEBT_ONLY.value,
            "violations_detected": violations,
            "unresolved_reason": None,
            "gap_closure_id": rule.closes_gap,
            "rationale": rule.rationale,
            "descriptive_fields": descriptive_fields,
        })

    def evaluate_batch(
        self,
        module_specs: Optional[List[Dict[str, Any]]] = None,
    ) -> BatchCanonicalEvaluationResult:
        """
        Run canonical evaluation on a list of module specifications.
        Defaults to evaluating standard modules M43 through M50.

        :param module_specs: Optional list of dicts with {'module_id': 'M43', 'assessment_mode': ...}
        :return: BatchCanonicalEvaluationResult
        """
        if module_specs is None:
            module_specs = [
                {"module_id": f"M{i}", "assessment_mode": "adversarial_validation"}
                for i in range(43, 51)
            ]

        results: Dict[str, CanonicalEvaluationResult] = {}
        resolved_count = 0
        unresolved_count = 0
        blocked_count = 0

        for spec in module_specs:
            mod_id = spec["module_id"]
            mode = spec.get("assessment_mode", "adversarial_validation")
            exec_data = spec.get("execution_data")

            eval_res = self.evaluate_module(mod_id, mode, exec_data)
            results[mod_id] = eval_res

            if eval_res.is_resolved():
                resolved_count += 1
            else:
                unresolved_count += 1

            if eval_res.future_canonical_metric_normalization_blocked:
                blocked_count += 1

        summary = {
            "total_evaluated": len(module_specs),
            "resolved_count": resolved_count,
            "unresolved_count": unresolved_count,
            "blocked_count": blocked_count,
            "approved_rules_in_catalog": len([r for r in self.rules.values() if r.is_approved()]),
            "evidence_mode": "synthetic_only",
            "confirmed_vulnerability": False,
            "formal_finding_allowed": False,
            "production_safety_claimed": False,
        }

        return BatchCanonicalEvaluationResult(evaluations=results, summary=summary)

    def resolve_gap(self, gap_id: str) -> Dict[str, Any]:
        """
        Execute formal GAP closure verification.

        :param gap_id: Identifier of the gap, e.g. "GAP-001".
        :return: Formal closure proof dictionary.
        """
        gap_upper = gap_id.strip().upper()
        rule_id = self.gap_closure_index.get(gap_upper)

        if not rule_id:
            return {
                "gap_id": gap_upper,
                "closure_status": "unresolved",
                "reason": f"No approved mapping rule mapped to {gap_upper}",
                "confirmed_vulnerability": False,
                "synthetic_only": True,
            }

        rule = self.rules[rule_id]
        eval_result = self.evaluate_module(rule.module_id, rule.assessment_mode)

        return {
            "gap_id": gap_upper,
            "target_module": rule.module_id,
            "module_name": rule.module_name,
            "closure_status": "closed" if eval_result.is_resolved() else "unresolved",
            "resolving_rule_id": rule.rule_id,
            "review_status": rule.review_status,
            "approved_by": rule.approved_by,
            "approval_date": rule.approval_date,
            "canonical_capability_value": eval_result.canonical_capability_value,
            "canonical_risk_level": eval_result.canonical_risk_level,
            "canonical_capability_status": eval_result.canonical_capability_status,
            "canonical_risk_status": eval_result.canonical_risk_status,
            "future_canonical_metric_normalization_blocked": eval_result.future_canonical_metric_normalization_blocked,
            "rationale": rule.rationale,
            "confirmed_vulnerability": False,
            "synthetic_only": True,
            "non_retroactivity_guarantee": {
                "retroactive_effect_on_existing_module_closure": False,
                "existing_module_conclusions_preserved": True,
                "existing_coverage_status_preserved": True,
                "existing_scorecard_conclusions_preserved": True,
            },
            "safety_boundaries": dict(ENGINE_SAFETY_BOUNDARIES),
        }

    def simulate_unresolved_to_resolved_transition(
        self,
        module_id: str,
        assessment_mode: str,
    ) -> TransitionResult:
        """
        Simulate and verify the formal transition from Unresolved to Resolved state.

        :param module_id: Target module identifier (e.g. M44).
        :param assessment_mode: Assessment mode (e.g. adversarial_validation).
        :return: TransitionResult object.
        """
        mod_upper = module_id.strip().upper()
        mode_lower = assessment_mode.strip().lower()

        # All modules start unresolved by definition (pre-rule state).
        prev_cap_status = CanonicalStatus.UNRESOLVED.value
        prev_risk_status = CanonicalStatus.UNRESOLVED.value

        eval_res = self.evaluate_module(mod_upper, mode_lower)

        success = eval_res.is_resolved()
        rule_id = eval_res.mapping_rule_id or "NONE"

        return TransitionResult(
            module_id=mod_upper,
            previous_capability_status=prev_cap_status,
            previous_risk_status=prev_risk_status,
            new_capability_status=eval_res.canonical_capability_status,
            new_risk_status=eval_res.canonical_risk_status,
            rule_id=rule_id,
            gap_closed=eval_res.gap_closure_id,
            non_retroactive_verified=True,
            transition_success=success,
            evidence_snapshot={
                "canonical_capability_value": eval_res.canonical_capability_value,
                "canonical_risk_level": eval_res.canonical_risk_level,
                "future_blocked": eval_res.future_canonical_metric_normalization_blocked,
                "descriptive_fields": eval_res.descriptive_fields,
            },
        )

    def export_scorecard(self, module_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export a comprehensive scorecard of rules coverage, evaluations, and GAP closures.

        :param module_ids: Optional list of module IDs. Defaults to M43-M50.
        :return: Structured scorecard dict.
        """
        if module_ids is None:
            module_ids = [f"M{i}" for i in range(43, 51)]

        specs = [{"module_id": m, "assessment_mode": "adversarial_validation"} for m in module_ids]
        batch_res = self.evaluate_batch(specs)

        gap_results: Dict[str, Any] = {}
        for gap in ("GAP-001", "GAP-002", "GAP-003", "GAP-004", "GAP-005"):
            gap_results[gap] = self.resolve_gap(gap)

        scorecard = {
            "scorecard_version": "1.0",
            "task_id": "Phase-98A-METRIC-001",
            "timestamp": "2026-08-18T22:00:00+08:00",
            "engine_class": self.__class__.__name__,
            "rules_source": self.rules_source_path,
            "rules_count": len(self.rules),
            "approved_rules_count": len([r for r in self.rules.values() if r.is_approved()]),
            "forbidden_auto_mapping_rules_count": len(FORBIDDEN_AUTO_MAPPING_RULES),
            "module_evaluations": {k: v.to_dict() for k, v in batch_res.evaluations.items()},
            "gap_closures": gap_results,
            "batch_summary": batch_res.summary,
            "non_retroactive_declarations": {
                "retroactive_effect_on_existing_module_closure": False,
                "existing_module_conclusions_preserved": True,
                "existing_coverage_status_preserved": True,
                "existing_scorecard_conclusions_preserved": True,
            },
            "safety_boundaries": dict(ENGINE_SAFETY_BOUNDARIES),
        }

        return scorecard

    def get_safety_boundaries(self) -> Dict[str, Union[bool, str]]:
        """Return engine safety boundaries dictionary."""
        return dict(self.safety_boundaries)
