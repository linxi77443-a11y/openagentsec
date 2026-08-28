import os
import sys
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.engine.v2 import ENGINE_VERSION
from src.engine.v2.safety_invariants import assert_safety_invariants
from src.engine.v2.run_spec import parse_run_spec, validate_run_spec
from src.engine.v2.converter import Base64Converter, LeetspeakConverter, ConverterChain
from src.engine.v2.orchestrator import MockProvider, CrescendoStrategy
from src.engine.v2.scorer import BooleanScorer, LikertScorer, CompositeAndScorer
from src.engine.v2.memory import JsonlMemory

def main():
    assert_safety_invariants()
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'run_configs', 'phase110b_engine003_run_config.yaml')
    spec = parse_run_spec(config_path)
    validate_run_spec(spec)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    memory_path = os.path.join(os.path.dirname(__file__), '..', 'executions', 'phase110b_engine003', 'trace.jsonl')
    memory = JsonlMemory(memory_path)

    converter_chain = ConverterChain([Base64Converter(), LeetspeakConverter()])
    provider = MockProvider()
    composite_scorer = CompositeAndScorer([BooleanScorer(), LikertScorer()])

    results = []

    for task in config_data['tasks']:
        orchestrator = CrescendoStrategy(provider, converter_chain)
        trace = orchestrator.run(task['prompt'])
        score_res = composite_scorer.score(trace)
        
        record = {
            "engine_version": ENGINE_VERSION,
            "task_id": task['task_id'],
            "atlas_technique_id": task['atlas_technique_id'],
            "intent": task['intent'],
            "converter_chain": orchestrator.converter_chain.get_chain_metadata() if orchestrator.converter_chain else [],
            "orchestrator": spec.orchestrator_strategy,
            "trace": trace,
            "score": score_res.score,
            "passed": score_res.passed,
            "rationale": score_res.rationale
        }
        memory.append(record)
        results.append(record)

    summary_path = os.path.join(os.path.dirname(__file__), '..', 'executions', 'phase110b_engine003', 'execution_summary.yaml')
    
    passed_count = sum(1 for r in results if r['passed'])
    total_count = len(results)
    
    summary = {
        "workplan_id": "Phase-110B-ENGINE-003",
        "release_tag": "v5.1.0-ENGINE003",
        "engine_version": ENGINE_VERSION,
        "safety_claim": {
            "synthetic_only": True,
            "fake_runtime_only": True,
            "requires_human_review": True
        },
        "capability_scorecard": {
            "total_tasks": total_count,
            "passed_tasks": passed_count,
            "overall_pass_rate": passed_count / total_count if total_count > 0 else 0.0,
            "task_results": [
                {
                    "task_id": r["task_id"],
                    "passed": r["passed"],
                    "score": r["score"]
                } for r in results
            ]
        }
    }
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        yaml.dump(summary, f, default_flow_style=False)

    print("Demo execution completed successfully.")

if __name__ == '__main__':
    main()
