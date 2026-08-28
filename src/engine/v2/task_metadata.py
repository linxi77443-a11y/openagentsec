import yaml
from dataclasses import dataclass
from enum import Enum
import os

from .safety_invariants import assert_safety_invariants

class Intent(Enum):
    ATTACK_SIMULATION = "attack_simulation"
    BENIGN_BASELINE = "benign_baseline"
    CALIBRATION = "calibration"

@dataclass
class TaskMetadata:
    task_id: str
    atlas_technique_id: str
    intent: Intent
    source_playbook: str
    expected_outcome: str

def load_task_metadata(path: str) -> TaskMetadata:
    assert_safety_invariants()
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    atlas_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'atlas', 'atlas_techniques.yaml')
    if os.path.exists(atlas_path):
        with open(atlas_path, 'r', encoding='utf-8') as f:
            atlas_data = yaml.safe_load(f)
        # 兼容顶层 list 与 dict（{"techniques": [...] 或 {...}}）两种结构
        if isinstance(atlas_data, dict):
            techniques = atlas_data.get('techniques', [])
        else:
            techniques = atlas_data or []
        if isinstance(techniques, dict):
            techniques = [
                dict({'technique_id': k}, **(v if isinstance(v, dict) else {}))
                for k, v in techniques.items()
            ]
        valid_ids = {
            item.get('technique_id')
            for item in techniques
            if isinstance(item, dict) and item.get('technique_id')
        }
        if data.get('atlas_technique_id') not in valid_ids:
            raise ValueError(f"Invalid atlas_technique_id: {data.get('atlas_technique_id')}")

    return TaskMetadata(
        task_id=data['task_id'],
        atlas_technique_id=data['atlas_technique_id'],
        intent=Intent(data['intent']),
        source_playbook=data['source_playbook'],
        expected_outcome=data['expected_outcome']
    )
