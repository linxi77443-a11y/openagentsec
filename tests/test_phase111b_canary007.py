import pytest
from src.engine.v2.canary import inject, detect, audit

def test_inject_format():
    token = inject("M03", "test-uuid")
    assert token == "<SIM_CANARY_test-uuid_M03>"

def test_inject_no_uuid():
    token1 = inject("M20")
    token2 = inject("M20")
    assert token1 != token2
    assert "<SIM_CANARY_" in token1
    assert "_M20>" in token1

def test_detect_single():
    text = "Here is a token: <SIM_CANARY_123_M03>"
    tokens = detect(text)
    assert len(tokens) == 1
    assert tokens[0] == "<SIM_CANARY_123_M03>"

def test_detect_multiple():
    text = "<SIM_CANARY_1_M03> and <SIM_CANARY_2_M20>"
    tokens = detect(text)
    assert len(tokens) == 2

def test_detect_none():
    text = "No canary here"
    assert len(detect(text)) == 0

def test_audit_hit():
    text = "Got <SIM_CANARY_abc_M03>"
    res = audit(text, "abc")
    assert res["hit"] is True
    assert res["cross_scenario_fp"] is False
    assert res["candidate"] is True

def test_audit_miss():
    text = "Nothing here"
    res = audit(text, "abc")
    assert res["hit"] is False
    assert res["cross_scenario_fp"] is False

def test_audit_cross_scenario_fp():
    text = "Got <SIM_CANARY_wrong-uuid_M03>"
    res = audit(text, "correct-uuid")
    assert res["hit"] is False
    assert res["cross_scenario_fp"] is True

def test_audit_hit_and_fp():
    text = "Got <SIM_CANARY_abc_M03> and <SIM_CANARY_def_M03>"
    res = audit(text, "abc")
    assert res["hit"] is True
    assert res["cross_scenario_fp"] is True

def test_audit_uuid_extraction():
    text = "<SIM_CANARY_1234-5678_MOD>"
    res = audit(text, "1234-5678")
    assert "1234-5678" in res["found_uuids"]

def test_audit_ignores_malformed():
    text = "<SIM_CANARY_incomplete>"
    res = audit(text, "incomplete")
    # Will not match the regex, so hit = False
    assert res["hit"] is False
