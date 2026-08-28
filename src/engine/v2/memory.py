import json
import os
from typing import Dict, Any
from datetime import datetime

from .safety_invariants import assert_safety_invariants

class JsonlMemory:
    def __init__(self, file_path: str):
        self.file_path = file_path
        os.makedirs(os.path.dirname(os.path.abspath(self.file_path)), exist_ok=True)

    def append(self, record: Dict[str, Any]) -> None:
        assert_safety_invariants()
        
        required_keys = ["engine_version", "task_id", "atlas_technique_id", "intent"]
        for key in required_keys:
            if key not in record or record[key] is None or str(record[key]).strip() == "":
                raise ValueError(f"Missing required field in memory record: {key}")
                
        record["timestamp"] = datetime.now().isoformat()
        record["safety_invariants_asserted"] = True
        
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
