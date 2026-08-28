import logging
from typing import Dict, List, Any
from src.engine.v2.safety_invariants import assert_safety_invariants

logger = logging.getLogger(__name__)

class ControlMetrics:
    def __init__(self, interception_rate: float, benign_usability: float, false_positive_rate: float):
        self.interception_rate = interception_rate
        self.benign_usability = benign_usability
        self.false_positive_rate = false_positive_rate

class ControlComparisonEngine:
    def __init__(self, baseline_metrics: ControlMetrics):
        assert_safety_invariants()
        self.baseline = baseline_metrics
        self.groups: Dict[str, ControlMetrics] = {}

    def add_group(self, name: str, metrics: ControlMetrics):
        assert_safety_invariants()
        self.groups[name] = metrics

    def compare(self) -> Dict[str, Dict[str, float]]:
        assert_safety_invariants()
        results = {}
        for name, metrics in self.groups.items():
            results[name] = {
                "interception_rate_increment": metrics.interception_rate - self.baseline.interception_rate,
                "benign_usability_loss": self.baseline.benign_usability - metrics.benign_usability,
                "false_positive_increment": metrics.false_positive_rate - self.baseline.false_positive_rate
            }
        return results

    def get_best_group(self, priority: str = "interception") -> str:
        assert_safety_invariants()
        if not self.groups:
            return ""
        
        best_group = ""
        best_score = -float('inf')

        for name, metrics in self.groups.items():
            score = 0.0
            if priority == "interception":
                score = metrics.interception_rate - metrics.false_positive_rate
            elif priority == "usability":
                score = metrics.benign_usability - metrics.false_positive_rate
            
            if score > best_score:
                best_score = score
                best_group = name
                
        return best_group
