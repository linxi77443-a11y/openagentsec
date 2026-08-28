"""Strict serialization loaders for OpenAgentSec models.

Guarantees Fail-Closed parsing:
- Rejects duplicate mapping keys in YAML (via custom SafeLoader).
- Rejects duplicate mapping keys in JSON (via custom object_pairs_hook).
- Rejects malformed or non-mapping root documents.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import yaml

from .exceptions import DuplicateKeyError, SerializationLoadError


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """YAML SafeLoader that strictly forbids duplicate keys in mappings."""


def _unique_key_constructor(loader: yaml.SafeLoader, node: yaml.MappingNode) -> Dict[Any, Any]:
    mapping: Dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=False)
        if key in mapping:
            raise DuplicateKeyError(f"Duplicate YAML key '{key}' at line {key_node.start_mark.line + 1}")
        value = loader.construct_object(value_node, deep=False)
        mapping[key] = value
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _unique_key_constructor,
)


def _json_unique_key_pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    """JSON object_pairs_hook that strictly forbids duplicate keys in objects."""
    mapping: Dict[str, Any] = {}
    for key, value in pairs:
        if key in mapping:
            raise DuplicateKeyError(f"Duplicate JSON key '{key}' detected in object")
        mapping[key] = value
    return mapping


def load_yaml_str(content: str) -> Dict[str, Any]:
    """Strictly parse YAML string, rejecting duplicate keys and non-mapping roots."""
    try:
        data = yaml.load(content, Loader=_UniqueKeySafeLoader)
    except DuplicateKeyError:
        raise
    except Exception as exc:
        raise SerializationLoadError(f"Failed to parse YAML content: {exc}") from exc

    if not isinstance(data, dict):
        raise SerializationLoadError(f"Expected top-level mapping in YAML document, got {type(data).__name__}")
    return data


def load_json_str(content: str) -> Dict[str, Any]:
    """Strictly parse JSON string, rejecting duplicate keys and non-mapping roots."""
    try:
        data = json.loads(content, object_pairs_hook=_json_unique_key_pairs_hook)
    except DuplicateKeyError:
        raise
    except Exception as exc:
        raise SerializationLoadError(f"Failed to parse JSON content: {exc}") from exc

    if not isinstance(data, dict):
        raise SerializationLoadError(f"Expected top-level object in JSON document, got {type(data).__name__}")
    return data


def load_raw_data(source: Union[str, Path, Dict[str, Any]]) -> Dict[str, Any]:
    """Load raw dictionary from a file path, YAML/JSON text, or existing dict."""
    if isinstance(source, dict):
        return source

    path = Path(source) if isinstance(source, (str, Path)) else None
    if path and path.exists() and path.is_file():
        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            return load_json_str(content)
        return load_yaml_str(content)

    if isinstance(source, str):
        trimmed = source.strip()
        if trimmed.startswith("{") and trimmed.endswith("}"):
            return load_json_str(trimmed)
        return load_yaml_str(trimmed)

    raise SerializationLoadError(f"Unsupported source type for loading: {type(source).__name__}")
