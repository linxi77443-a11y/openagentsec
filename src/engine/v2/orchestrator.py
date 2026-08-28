from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from .safety_invariants import assert_safety_invariants
from .converter import ConverterChain

class MockProvider:
    def __init__(self):
        self.responses = [
            "<SIM_MOCK_RESPONSE_1> I cannot fulfill this request.",
            "<SIM_MOCK_RESPONSE_2> Sure, here is the secret: <SIM_SECRET>.",
            "<SIM_MOCK_RESPONSE_3> Here is the simulated payload: <SIM_PAYLOAD>",
        ] * 5

    def get_response(self, prompt: str) -> str:
        import random
        return random.choice(self.responses)

class BaseOrchestrator(ABC):
    def __init__(self, provider: MockProvider, converter_chain: Optional[ConverterChain] = None):
        self.provider = provider
        self.converter_chain = converter_chain
        self.trace: List[Dict[str, Any]] = []

    @abstractmethod
    def run(self, initial_prompt: str) -> List[Dict[str, Any]]:
        pass

    def record_turn(self, round_number: int, prompt: str, response: str) -> None:
        assert_safety_invariants()
        record = {
            "round_number": round_number,
            "converter_chain": self.converter_chain.get_chain_metadata() if self.converter_chain else [],
            "mock_response_id": f"sim_resp_{round_number}",
            "prompt": prompt,
            "response": response,
            "safety_invariants_asserted": True
        }
        self.trace.append(record)

class SingleTurnStrategy(BaseOrchestrator):
    def run(self, initial_prompt: str) -> List[Dict[str, Any]]:
        assert_safety_invariants()
        prompt = self.converter_chain.convert(initial_prompt) if self.converter_chain else initial_prompt
        response = self.provider.get_response(prompt)
        self.record_turn(1, prompt, response)
        return self.trace

class CrescendoStrategy(BaseOrchestrator):
    def run(self, initial_prompt: str) -> List[Dict[str, Any]]:
        assert_safety_invariants()
        for i in range(1, 6):
            prompt = f"{initial_prompt} (Round {i})"
            converted_prompt = self.converter_chain.convert(prompt) if self.converter_chain else prompt
            response = self.provider.get_response(converted_prompt)
            self.record_turn(i, converted_prompt, response)
            if "<SIM_SECRET>" in response or "<SIM_PAYLOAD>" in response:
                break
        return self.trace

class TAPTreeSearchStrategy(BaseOrchestrator):
    def run(self, initial_prompt: str) -> List[Dict[str, Any]]:
        assert_safety_invariants()
        round_num = 1
        for depth in range(3):
            prompt = f"{initial_prompt} (Depth {depth})"
            converted_prompt = self.converter_chain.convert(prompt) if self.converter_chain else prompt
            response = self.provider.get_response(converted_prompt)
            self.record_turn(round_num, converted_prompt, response)
            round_num += 1
        return self.trace
