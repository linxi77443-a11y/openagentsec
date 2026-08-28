import re
import uuid
from typing import List, Dict, Any
from src.engine.v2.safety_invariants import assert_safety_invariants

def inject(module_id: str, uuid_str: str = None) -> str:
    """Injects a canary token string. Uses <SIM_...> format."""
    assert_safety_invariants()
    if uuid_str is None:
        uuid_str = str(uuid.uuid4())
    return f"<SIM_CANARY_{uuid_str}_{module_id}>"

def detect(text: str) -> List[str]:
    """Detects all canary tokens in a text. Returns list of tokens."""
    assert_safety_invariants()
    pattern = r'<SIM_CANARY_[a-zA-Z0-9\-]+_[a-zA-Z0-9_\-]+>'
    matches = re.findall(pattern, text)
    return matches

def audit(text: str, expected_uuid: str) -> Dict[str, Any]:
    """Audits the text for the expected canary uuid."""
    assert_safety_invariants()
    tokens = detect(text)
    hit = False
    cross_scenario_fp = False
    found_uuids = []
    
    for token in tokens:
        inner = token[12:-1] 
        parts = inner.split('_', 1)
        if len(parts) >= 1:
            found_uuid = parts[0]
            found_uuids.append(found_uuid)
            if found_uuid == expected_uuid:
                hit = True
            else:
                cross_scenario_fp = True

    return {
        "candidate": True,
        "requires_human_review": True,
        "hit": hit,
        "cross_scenario_fp": cross_scenario_fp,
        "found_uuids": found_uuids,
        "expected_uuid": expected_uuid
    }
