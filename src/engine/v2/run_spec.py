import yaml
from dataclasses import dataclass
from typing import List

from .safety_invariants import assert_safety_invariants

@dataclass
class RunSpec:
    module: str
    mode: str
    converter_chain_names: List[str]
    orchestrator_strategy: str
    scorer_types: List[str]

def parse_run_spec(path: str) -> RunSpec:
    assert_safety_invariants()
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    return RunSpec(
        module=data.get('module', ''),
        mode=data.get('mode', ''),
        converter_chain_names=data.get('converter_chain', []),
        orchestrator_strategy=data.get('orchestrator_strategy', ''),
        scorer_types=data.get('scorer_types', [])
    )

def validate_run_spec(spec: RunSpec) -> bool:
    assert_safety_invariants()
    valid_converters = {"Base64Converter", "ROT13Converter", "LeetspeakConverter", "ReverseTextConverter", "TranslationPlaceholderConverter"}
    valid_orchestrators = {"SingleTurnStrategy", "CrescendoStrategy", "TAPTreeSearchStrategy"}
    valid_scorers = {"BooleanScorer", "LikertScorer", "RubricScorer", "CompositeAndScorer"}

    for c in spec.converter_chain_names:
        if c not in valid_converters:
            raise ValueError(f"Invalid converter: {c}")
    
    if spec.orchestrator_strategy not in valid_orchestrators:
        raise ValueError(f"Invalid orchestrator strategy: {spec.orchestrator_strategy}")

    for s in spec.scorer_types:
        if s not in valid_scorers:
            raise ValueError(f"Invalid scorer: {s}")

    return True
