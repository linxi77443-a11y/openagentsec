# OpenAgentSec Quick Start Guide (15-Minute Onboarding)

**Version: 1.0.0**  
**Document ID: OAS-DOC-QUICKSTART-001**

Research status: [docs/research/README.md](../research/README.md). Live DeepSeek tests stay skipped unless `OPENAGENTSEC_ENABLE_LIVE_TESTS=true`. Planner tests are **simulation/pipeline**, not live Agent validation.

---

## 1. Environment & Prerequisites

- **Python Version**: Python 3.10, 3.11, or 3.12.
- **Operating System**: macOS, Linux, or Windows (WSL2).

### Clone and Install
```bash
# Clone the repository
git clone https://github.com/linxi77443-a11y/openagentsec.git
cd openagentsec

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies in editable mode
pip install -e .
pip install pytest pyyaml jsonschema
```

---

## 2. Running Benchmark Evaluation Tests

OpenAgentSec includes a non-live regression suite for evaluation-lifecycle contracts (Oracle decision consistency is not the same as fully deterministic Agent behavior). Planner tests below are **simulation/pipeline**, not live Agent validation:

### Step A: Run Core Benchmark Integration Suite
```bash
pytest tests/integration/planner/ -v
```
*Expected: All planner tests pass in ~5.0s.*

### Step B: Run Full Unit & Integration Test Suites
```bash
# Non-live unit + integration. Live DeepSeek / paid API tests skip unless gated env vars are set.
# Do not treat a historical count (e.g. 204/278) as current suite size.
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/integration/ -v
```

### Step C: Run Real-world Empirical Validation (LangGraph & MCP)
```bash
pytest tests/integration/empirical/ -v
```
*Expected: 14 passed (EXP-REAL-001 ~ 005).*

### Step D: Regenerating and Verifying Research Artifacts
```bash
# 1. Regenerate all JSON artifacts and schemas
python3 scripts/generate_research_artifacts.py

# 2. Run the official one-click release verification script
bash scripts/verify_release.sh
```

---

## 3. Extending the Framework

### A. How to Add a New Target Adapter
1. Subclass `BlackboxTargetAdapter` in `tests/integration/external_targets/`:
```python
from tests.integration.external_targets.langchain.adapter import BlackboxTargetAdapter
from targets.api.target_adapter import TargetResponse
from src.openagentsec.oracle.evidence import EvidenceItem

class CustomAgentAdapter(BlackboxTargetAdapter):
    def send_message(self, user_input: str, session_id: Optional[str] = None) -> TargetResponse:
        # Send input to your custom agent runtime
        ...
    def observe_tool_execution(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        # Return verified tool execution logs
        ...
    def collect_evidence(self, step_id: str, run_id: str) -> List[EvidenceItem]:
        # Package runtime logs into EvidenceItem instances
        ...
    def reset_session(self, session_id: Optional[str] = None, clean_state: bool = True) -> bool:
        # Clean state between reproduction runs
        ...
```
2. Register the target in `src/openagentsec/benchmark/target_catalog.py`.

### B. How to Register a New Scenario
Add an entry in `src/openagentsec/benchmark/scenario_registry.py`:
```python
from src.openagentsec.benchmark.scenario_registry import BenchmarkScenario, ScenarioRegistry

ScenarioRegistry.register(
    BenchmarkScenario(
        scenario_id="CUSTOM-ATTACK-001",
        domain="authorization_security",
        title="Custom Perimeter Bypass Test",
        attack_type="perimeter_bypass",
        description="Evaluates whether agent can bypass custom firewall rules.",
        required_capabilities=["policy_enforcement_point"],
        evaluation_operator="tool_boundary_check",
    )
)
```

### C. How to Register a New Metric
Add an entry in `src/openagentsec/benchmark/metric_registry.py`:
```python
from src.openagentsec.benchmark.metric_registry import BenchmarkMetric, MetricRegistry

MetricRegistry.register(
    BenchmarkMetric(
        metric_id="custom_mitigation_rate",
        domain="governance",
        name="Custom Mitigation Rate",
        unit="ratio",
        description="Measures proportion of custom attack vectors mitigated by policy firewall.",
        formula="mitigated_attacks / total_attacks",
        statutory_range=(0.0, 1.0),
    )
)
```
