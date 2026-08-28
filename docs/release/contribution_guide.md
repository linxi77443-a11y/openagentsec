# Contributing to OpenAgentSec

Thank you for contributing to OpenAgentSec! We welcome contributions to expand target adapters, adversarial evaluation scenarios, security metrics, and evidence models.

---

## 1. Contribution Categories

### A. Adding a New Target Adapter
- Implement the `BlackboxTargetAdapter` interface in `targets/api/` or `tests/integration/external_targets/`.
- Ensure clean session reset logic (`reset_session(clean_state=True)`).
- Register the target profile in `src/openagentsec/benchmark/target_catalog.py`.

### B. Adding a New Adversarial Scenario
- Define the new scenario in `src/openagentsec/benchmark/scenario_registry.py`.
- Assign a unique `scenario_id` (e.g. `MEM-CUSTOM-001`, `AUTH-CUSTOM-001`).
- Specify required capabilities, expected evidence types, and oracle rules.

### C. Adding a New Metric
- Define the metric in `src/openagentsec/benchmark/metric_registry.py`.
- Provide an exact mathematical formula, unit, definition, and target applicability mapping.

### D. Adding a New Evidence Type
- Register the evidence requirement in `src/openagentsec/benchmark/evidence_contract.py`.
- Ensure provenance sources and validation semantics are documented.

---

## 2. Pull Request (PR) Requirements

Every Pull Request must satisfy the following criteria before merging:
1. **Automated Tests**:
   - Provide an integration test in `tests/integration/planner/`.
   - All tests in `pytest tests/integration/planner/ -v` must pass (157+ passed).
2. **Statutory Reproduction**:
   - Adversarial scenarios must include a 5-run statutory reproduction test (`ReproductionAggregator.aggregate`).
3. **No LLM Judge**:
   - Do not introduce subjective natural language LLM judges; use `DeterministicToolBoundaryOracle` or invariant-based oracles.
4. **Documentation**:
   - Update `docs/research/benchmark_specification.md` and `docs/release/benchmark_results.md`.

---

## 3. Code Quality & Standards

- **Type Annotations**: Strict typing with `from __future__ import annotations` and PEP 484 annotations.
- **Fail-Closed Principle**: Any ambiguous or degraded state must default to `INCONCLUSIVE`.
- **Zero Network Side Effects**: All tests must execute locally against mocks, sandbox tools, or gateway proxies (`synthetic_only: true`).
