import base64
import codecs
from abc import ABC, abstractmethod
from typing import List

from .safety_invariants import assert_safety_invariants

class BaseConverter(ABC):
    @abstractmethod
    def convert(self, text: str) -> str:
        pass

class Base64Converter(BaseConverter):
    def convert(self, text: str) -> str:
        assert_safety_invariants()
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

class ROT13Converter(BaseConverter):
    def convert(self, text: str) -> str:
        assert_safety_invariants()
        return codecs.encode(text, 'rot_13')

class LeetspeakConverter(BaseConverter):
    def convert(self, text: str) -> str:
        assert_safety_invariants()
        replacements = {'a': '4', 'A': '4', 'e': '3', 'E': '3', 'i': '1', 'I': '1', 'o': '0', 'O': '0', 's': '5', 'S': '5', 't': '7', 'T': '7'}
        return ''.join(replacements.get(c, c) for c in text)

class ReverseTextConverter(BaseConverter):
    def convert(self, text: str) -> str:
        assert_safety_invariants()
        return text[::-1]

class TranslationPlaceholderConverter(BaseConverter):
    def convert(self, text: str) -> str:
        assert_safety_invariants()
        return f"<SIM_TRANSLATED>{text}</SIM_TRANSLATED>"

class ConverterChain:
    def __init__(self, converters: List[BaseConverter]):
        self.converters = converters
        
    def convert(self, text: str) -> str:
        assert_safety_invariants()
        result = text
        for converter in self.converters:
            result = converter.convert(result)
        return result

    def get_chain_metadata(self) -> List[str]:
        return [converter.__class__.__name__ for converter in self.converters]
