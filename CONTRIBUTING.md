# Contributing to OpenAgentSec

Thank you for your interest in contributing to **OpenAgentSec**! We welcome contributions from AI safety researchers, security engineers, and open-source practitioners.

Public repository: https://github.com/linxi77443-a11y/openagentsec

OpenAgentSec v1.x is a **research framework**. Claim source of truth: [`docs/research/README.md`](docs/research/README.md). Do not treat 5-run decision consistency as fully deterministic Agent behavior, and do not add production-scanner claims.

---

## 1. Governance Principles & Invariants

To maintain strict scientific reproducibility and enterprise reliability, all contributions must adhere to our core project invariants:

1. **Frozen Core Contracts**:
   - The core data structures (`SecurityPolicy`, `EvaluationObjective`, `EvidenceItem`, `DeterministicToolBoundaryOracle`, `ReproductionAggregator`) are **frozen** for the `v1.x` release series.
   - New framework integrations must be implemented via the `TargetAdapter` interface without modifying the core Oracle logic.
2. **Statutory 5-Run Zero-Variance Rule**:
   - Every newly added scenario or adapter test must achieve $\text{Variance} = 0.0000$ across 5 independent clean sessions. Flaky or non-deterministic tests cannot be merged.
3. **Calibrated Claim Standard**:
   - All documentation, docstrings, and PR descriptions must use objective, calibrated scientific language (see [`docs/research/claim_audit_final.md`](docs/research/claim_audit_final.md)). Unverifiable superlatives ("100% secure", "world-leading") are prohibited.

---

## 2. Development Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/linxi77443-a11y/openagentsec.git
cd openagentsec

# 2. Create isolated virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install in editable mode with development dependencies
pip install -e .
pip install pytest pyyaml jsonschema
```

---

## 3. How to Contribute

### A. Implementing a New Runtime TargetAdapter
If you want to add support for a new Agent framework (e.g. CrewAI, AutoGen, LlamaIndex):
1. Subclass `TargetAdapter` from `openagentsec.adapters.base`.
2. Implement telemetry capture returning typed `EvidenceItem` receipts (`tool_execution_log`, `authorization_check_receipt`, etc.).
3. Add a dedicated integration test under `tests/integration/real_world/` or `tests/integration/external_targets/`.
4. Ensure your adapter passes `test_external_adapter_contract.py`.
5. Refer to [`docs/release/contribution_guide.md`](docs/release/contribution_guide.md) and [`docs/release/contributor_experience_report.md`](docs/release/contributor_experience_report.md).

### B. Adding a New Security Scenario
1. Define the scenario in `artifact/benchmark/scenarios.json` conforming to `scenario.schema.yaml`.
2. Specify the explicit `SecurityPolicy` and `EvaluationObjective` requirements.
3. Add multi-turn prompt and context injection payloads.
4. Implement integration tests validating both vulnerable baseline and defended targets.

---

## 4. Pull Request Checklist

Before submitting your PR:
- [ ] All unit and integration tests pass: `PYTHONPATH=src pytest tests/unit tests/integration -v`.
- [ ] Release verification script passes: `bash scripts/verify_release.sh`.
- [ ] Code follows PEP 8 styling and contains type annotations (`mypy` / Python 3.10+ typing).
- [ ] Documentation and example files are updated if introducing new features.
- [ ] PR description clearly states the problem, solution, and provides test logs.

---

## 5. Code of Conduct

All contributors are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any violations to `conduct@openagentsec.org`.
