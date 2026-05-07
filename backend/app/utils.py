import re
from datetime import date
from typing import Any

VALID_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
DATE_KEYS = ("fecha", "date", "ultimo_uso", "desde", "actualizado")


def validate_name(value: str, kind: str = "identificador") -> str:
    if not value or not VALID_NAME.match(value):
        raise ValueError(f"{kind} inválido: {value}")
    return value


def cypher_label(label: str) -> str:
    return f"`{validate_name(label, 'label')}`"


def cypher_type(rel_type: str) -> str:
    return f"`{validate_name(rel_type, 'tipo de relación')}`"


def split_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [v.strip() for v in str(value).split("|") if v.strip()]


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "si", "sí", "yes", "y"}


def normalize_value(key: str, value: Any) -> Any:
    if value == "" or value is None:
        return None
    if isinstance(value, str):
        raw = value.strip()
        if raw.lower() in {"true", "false"}:
            return parse_bool(raw)
        if "|" in raw:
            return split_list(raw)
        if any(token in key.lower() for token in DATE_KEYS) and re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
            return date.fromisoformat(raw)
        return raw
    return value


def normalize_properties(properties: dict[str, Any]) -> dict[str, Any]:
    return {key: normalize_value(key, value) for key, value in properties.items() if value is not None and value != ""}
