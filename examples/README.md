# OpenAgentSec Developer Examples & Reference Implementations

**Directory Baseline**: `OpenAgentSec v1.0.0 GA`  

---

## 1. Available Examples

All examples are 100% self-contained in pure Python and run locally with zero external API dependencies or cloud costs:

| Example Script | Focus & Architecture Demonstrated | Execution Command |
|---|---|---|
| [`quickstart_eval.py`](quickstart_eval.py) | **Minimal Evaluation**: Policy definition, Deterministic Oracle invariant evaluation, and 5-run reproduction gate in under 45 lines. | `python3 examples/quickstart_eval.py` |
| [`custom_adapter_example.py`](custom_adapter_example.py) | **Custom Agent Adapter**: Implementing the canonical 9-method `TargetAdapter` ABC to wrap custom agents or APIs. | `python3 examples/custom_adapter_example.py` |
| [`end_to_end_eval.py`](end_to_end_eval.py) | **Flagship End-to-End Workflow**: Chaining `SecurityPolicy` + `EvaluationObjective` + `TargetAdapter` + `EvidenceItem` + `DeterministicToolBoundaryOracle` + `ReproductionAggregator`. | `python3 examples/end_to_end_eval.py` |

---

## 2. Running All Examples

```bash
# 1. Activate your virtual environment
source venv/bin/activate

# 2. Run the Minimal Quickstart
python3 examples/quickstart_eval.py

# 3. Run the Custom TargetAdapter Walkthrough
python3 examples/custom_adapter_example.py

# 4. Run the Full End-to-End Evaluation Workflow
python3 examples/end_to_end_eval.py
```
