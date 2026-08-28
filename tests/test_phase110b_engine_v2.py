import os
import pytest
import tempfile
import yaml

from src.engine.v2.safety_invariants import assert_safety_invariants, SafetyInvariantViolation, SAFETY_INVARIANTS
from src.engine.v2.converter import Base64Converter, ROT13Converter, LeetspeakConverter, ReverseTextConverter, TranslationPlaceholderConverter, ConverterChain
from src.engine.v2.orchestrator import MockProvider, SingleTurnStrategy, CrescendoStrategy, TAPTreeSearchStrategy
from src.engine.v2.scorer import BooleanScorer, LikertScorer, RubricScorer, CompositeAndScorer
from src.engine.v2.memory import JsonlMemory
from src.engine.v2.task_metadata import load_task_metadata, TaskMetadata, Intent
from src.engine.v2.run_spec import parse_run_spec, validate_run_spec, RunSpec

# --- Safety Invariants Tests ---

def test_safety_invariants_complete():
    assert_safety_invariants() # Should pass without exception

def test_safety_invariants_tampering(monkeypatch):
    monkeypatch.setitem(SAFETY_INVARIANTS, "synthetic_only", False)
    with pytest.raises(SafetyInvariantViolation):
        assert_safety_invariants()
    monkeypatch.delitem(SAFETY_INVARIANTS, "synthetic_only", raising=False)
    with pytest.raises(SafetyInvariantViolation):
        assert_safety_invariants()

# --- Converter Tests ---

def test_base64_converter():
    conv = Base64Converter()
    assert conv.convert("test") == "dGVzdA=="

def test_rot13_converter():
    conv = ROT13Converter()
    assert conv.convert("test") == "grfg"

def test_leetspeak_converter():
    conv = LeetspeakConverter()
    assert conv.convert("leet") == "l337"

def test_reverse_text_converter():
    conv = ReverseTextConverter()
    assert conv.convert("test") == "tset"

def test_translation_placeholder_converter():
    conv = TranslationPlaceholderConverter()
    assert conv.convert("test") == "<SIM_TRANSLATED>test</SIM_TRANSLATED>"

def test_converter_chain():
    chain = ConverterChain([ReverseTextConverter(), Base64Converter()])
    # reverse "test" -> "tset", base64 of "tset" -> "dHNldA=="
    assert chain.convert("test") == "dHNldA=="

def test_converter_reversibility_base64():
    import base64
    conv = Base64Converter()
    encoded = conv.convert("hello world")
    decoded = base64.b64decode(encoded).decode('utf-8')
    assert decoded == "hello world"

def test_converter_reversibility_rot13():
    conv = ROT13Converter()
    encoded = conv.convert("hello world")
    decoded = conv.convert(encoded) # rot13 is its own inverse
    assert decoded == "hello world"

# --- Orchestrator Tests ---

def test_single_turn_strategy():
    provider = MockProvider()
    strategy = SingleTurnStrategy(provider)
    trace = strategy.run("hello")
    assert len(trace) == 1
    assert trace[0]["round_number"] == 1

def test_crescendo_strategy():
    provider = MockProvider()
    strategy = CrescendoStrategy(provider)
    trace = strategy.run("hello")
    assert 1 <= len(trace) <= 5

def test_tap_tree_search_strategy():
    provider = MockProvider()
    strategy = TAPTreeSearchStrategy(provider)
    trace = strategy.run("hello")
    assert len(trace) == 3

def test_orchestrator_turn_recording():
    provider = MockProvider()
    strategy = SingleTurnStrategy(provider)
    trace = strategy.run("test prompt")
    assert trace[0]["prompt"] == "test prompt"
    assert "mock_response_id" in trace[0]
    assert trace[0]["safety_invariants_asserted"] is True

# --- Scorer Tests ---

def test_boolean_scorer():
    scorer = BooleanScorer()
    res = scorer.score([{"mock_response": "I refused"}])
    assert res.passed is False

def test_likert_scorer():
    scorer = LikertScorer()
    res = scorer.score([])
    assert res.score == 5.0

def test_rubric_scorer():
    scorer = RubricScorer()
    res = scorer.score([])
    assert res.passed is True

def test_composite_scorer():
    scorer = CompositeAndScorer([BooleanScorer(), LikertScorer()])
    res = scorer.score([{"mock_response": "ok"}])
    assert res.passed is True

# --- Memory Tests ---

def test_memory_missing_fields():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        mem = JsonlMemory(f.name)
        with pytest.raises(ValueError):
            mem.append({"engine_version": "5.1.0"}) # missing others

def test_memory_append():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        mem = JsonlMemory(f.name)
        mem.append({
            "engine_version": "5.1.0",
            "task_id": "t1",
            "atlas_technique_id": "a1",
            "intent": "attack"
        })
    with open(f.name, 'r') as f_read:
        lines = f_read.readlines()
        assert len(lines) == 1
        assert "timestamp" in lines[0]
        assert "safety_invariants_asserted" in lines[0]

# --- Task Metadata Tests ---

def test_task_metadata_load(tmp_path):
    p = tmp_path / "task.yaml"
    p.write_text(yaml.dump({
        "task_id": "t1",
        "atlas_technique_id": "atlas.llm_prompt_injection",
        "intent": "attack_simulation",
        "source_playbook": "p1",
        "expected_outcome": "pass"
    }))
    meta = load_task_metadata(str(p))
    assert meta.task_id == "t1"

def test_task_metadata_invalid_technique(tmp_path):
    p = tmp_path / "task.yaml"
    p.write_text(yaml.dump({
        "task_id": "t1",
        "atlas_technique_id": "invalid.technique",
        "intent": "attack_simulation",
        "source_playbook": "p1",
        "expected_outcome": "pass"
    }))
    with pytest.raises(ValueError):
        load_task_metadata(str(p))

# --- Run Spec Tests ---

def test_run_spec_parse(tmp_path):
    p = tmp_path / "spec.yaml"
    p.write_text(yaml.dump({
        "module": "m1",
        "mode": "s1",
        "converter_chain": ["Base64Converter"],
        "orchestrator_strategy": "SingleTurnStrategy",
        "scorer_types": ["BooleanScorer"]
    }))
    spec = parse_run_spec(str(p))
    assert spec.orchestrator_strategy == "SingleTurnStrategy"

def test_run_spec_validate():
    spec = RunSpec("m", "s", ["InvalidConverter"], "SingleTurnStrategy", ["BooleanScorer"])
    with pytest.raises(ValueError):
        validate_run_spec(spec)

# --- End to End Tests ---

def test_demo_script_execution():
    import subprocess
    script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'run_phase110b_engine003_demo.py')
    res = subprocess.run(["python3", script_path], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Demo execution completed successfully." in res.stdout

def test_trace_output():
    trace_path = os.path.join(os.path.dirname(__file__), '..', 'executions', 'phase110b_engine003', 'trace.jsonl')
    assert os.path.exists(trace_path)
    with open(trace_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) > 0
        import json
        record = json.loads(lines[0])
        assert record.get("engine_version") is not None
        assert record.get("task_id") is not None
        assert record.get("atlas_technique_id") is not None
        assert record.get("intent") is not None
