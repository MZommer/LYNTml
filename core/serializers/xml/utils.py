from abc import ABC
from collections.abc import Sequence
from typing import Any, get_args, get_origin


def parse_bool(raw: str) -> bool:
    match raw.strip().lower():
        case "true" | "1" | "yes":
            return True
        case "false" | "0" | "no":
            return False
        case _:
            raise ValueError(f"Cannot convert {raw!r} to bool")


def type_arg[T](annotation: type[T]) -> type[T]:
    if not (args := get_args(annotation)):
        msg = f"Missing type parameter in {annotation!r}"
        raise TypeError(msg)
    return args[0]


def is_descriptor(obj: Any) -> bool:
    return hasattr(type(obj), "__set__") or hasattr(type(obj), "__get__")


def all_hints(cls: type) -> dict:
    """Collect annotations from cls and all its XMLElement bases in MRO order,
    with subclass annotations taking precedence (subclass appears earlier in MRO,
    so we iterate reversed to let later entries overwrite earlier ones).
    Stops at — and excludes — XMLElement itself so framework internals are never
    included in field hints.
    """
    hints: dict = {}
    for base in reversed(cls.__mro__):
        # Stop before XMLElement so its own class-level attrs aren't treated as fields.
        if base.__name__ == "XMLElement" or base is object or base is ABC:
            continue
        hints.update(vars(base).get("__annotations__", {}))
    return hints


def resolve_dtype(dtype: type) -> tuple[bool, type]:
    """Unpack a field's dtype into (is_sequence, item_type).

    Examples:
        float        -> (False, float)
        list[float]  -> (True,  float)
        list[str]    -> (True,  str)

    """
    if get_origin(dtype) is list:
        args = get_args(dtype)
        return True, (args[0] if args else str)
    return False, dtype


def typecheck(value: Any, dtype: type, field: str = "") -> None:
    """Runtime type-check a value against dtype, supporting list[T]."""
    is_seq, item_type = resolve_dtype(dtype)
    if item_type is Any:
        return
    prefix = f"{field}: " if field else ""
    if is_seq:
        if not isinstance(value, Sequence):
            raise TypeError(
                f"{prefix}expected list[{item_type.__name__}],"
                " got {type(value).__name__}"
            )
        for i, v in enumerate(value):
            if not isinstance(v, item_type):
                raise TypeError(
                    f"{prefix}list item [{i}]: expected {item_type.__name__}, "
                    f"got {type(v).__name__}"
                )
    elif not isinstance(value, dtype):
        raise TypeError(
            f"{prefix}expected {dtype.__name__}, got {type(value).__name__}"
        )


SEQ_SEP = ";"  # separator used for comma-separated sequences in XML


def to_str(value: Any, dtype: type) -> str:
    """Encode a Python value to its XML text representation."""
    is_seq, _item_type = resolve_dtype(dtype)
    if is_seq:
        return SEQ_SEP.join(str(v) for v in value)
    if issubclass(dtype, float) and not value % 1:
        value = int(value)
    return str(value)


def from_str(raw: str, dtype: type) -> Any:
    """Decode an XML text value to the Python type described by dtype."""
    is_seq, item_type = resolve_dtype(dtype)
    if is_seq:
        if not raw.strip():
            return []
        return [from_scalar(part.strip(), item_type) for part in raw.split(SEQ_SEP)]
    return from_scalar(raw, dtype)


def from_scalar(raw: str, dtype: type) -> Any:
    """Decode a single scalar string to dtype."""
    if dtype is bool:
        return parse_bool(raw)
    try:
        return dtype(raw)
    except (ValueError, TypeError) as exc:
        msg = f"Cannot convert {raw!r} to {dtype.__name__}: {exc}"
        raise TypeError(msg) from exc
