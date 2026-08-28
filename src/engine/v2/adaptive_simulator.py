from typing import Dict, Any, List
from src.engine.v2.safety_invariants import assert_safety_invariants

class AdaptiveSimulator:
    """
    Simulates an adaptive attacker adjusting based on defense feedback.
    Purely a state machine. Only consumes existing playbook samples + mock responses.
    DOES NOT generate new payloads.
    """
    def __init__(self, scenarios: List[Dict[str, Any]]):
        self.scenarios = scenarios
        self.results = []
    
    def run_adaptive_simulation(self) -> Dict[str, Any]:
        assert_safety_invariants()
        
        static_success_count = 0
        adaptive_success_count = 0
        total = len(self.scenarios)
        
        for scenario in self.scenarios:
            scenario_id = scenario.get("id", "unknown")
            static_payload = scenario.get("static_payload", "<SIM_PAYLOAD_STATIC>")
            adaptive_variants = scenario.get("adaptive_variants", [])
            defense_feedback = scenario.get("defense_feedback", "block")
            
            # Static pass
            static_success = False
            if defense_feedback != "block":
                static_success = True
                static_success_count += 1
            
            # Adaptive pass (state machine)
            adaptive_success = False
            current_feedback = defense_feedback
            
            for variant in adaptive_variants:
                # Mock processing variant
                if current_feedback == "block" and variant.get("bypasses_block", False):
                    adaptive_success = True
                    break
                elif variant.get("always_success", False):
                    adaptive_success = True
                    break
            
            if adaptive_success:
                adaptive_success_count += 1
                
            self.results.append({
                "scenario_id": scenario_id,
                "static_success": static_success,
                "adaptive_success": adaptive_success,
                "requires_human_review": True,
                "status": "candidate"
            })
            
        return {
            "total_scenarios": total,
            "static_success_rate": static_success_count / total if total > 0 else 0,
            "adaptive_success_rate": adaptive_success_count / total if total > 0 else 0,
            "results": self.results,
            "requires_human_review": True,
            "status": "candidate"
        }
