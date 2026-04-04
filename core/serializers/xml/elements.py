from abc import ABC
from typing import Any, get_origin

from .descriptors import (
    XMLAttribute,
    XMLElementCollection,
    XMLSiblingCollection,
    XMLSubElement,
)
from .utils import is_descriptor


def _make_init(hints: dict, defaults: dict) -> callable:
    """Generate __init__ from schema annotations.

    Ordering (mirrors dataclass):
      1. Required fields (no default) — XMLSubElement / XMLAttribute only.
      2. Optional fields — those with defaults, plus all collections
         (XMLElementCollection and XMLSiblingCollection).

    All assignments route through descriptors -> type-checking is free.
    """

    def is_collection(ann):
        return get_origin(ann) in (
            XMLElementCollection,
            XMLSiblingCollection,
        ) or ann in (XMLElementCollection, XMLSiblingCollection)

    required = [
        (n, a) for n, a in hints.items() if n not in defaults and not is_collection(a)
    ]
    optional = [(n, a) for n, a in hints.items() if n in defaults or is_collection(a)]

    params = ["self"]
    body_lines = []

    for name, _ in required:
        params.append(name)
        body_lines.append(f"    self.{name} = {name}")

    for name, ann in optional:
        has_default = name in defaults

        if is_collection(ann):
            params.append(f"{name}=None")
            if has_default:
                body_lines.append(
                    f"    if {name} is None: {name} = list(__defs__['{name}'])\n"
                    f"    for _i in {name}: self.{name}.append(_i)"
                )
            else:
                body_lines.append(
                    f"    if {name} is not None:\n"
                    f"        for _i in {name}: self.{name}.append(_i)"
                )
        else:
            params.append(f"{name}=__defs__['{name}']")
            body_lines.append(f"    self.{name} = {name}")

    param_str = ", ".join(params)
    body = "\n".join(body_lines) if body_lines else "    pass"
    src = f"def __init__({param_str}):\n{body}"

    ns: dict = {"__defs__": defaults}
    exec(src, ns)  # noqa: S102
    return ns["__init__"]


class XMLElement(ABC):
    """Base for all XML-mapped elements.

    Subclasses get:
      • Descriptor instances auto-installed for every annotated field.
      • A type-checked __init__ auto-generated from the schema (unless one
        is already defined in the subclass body).
    """

    __lower_tag__ = False

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        hints = vars(cls).get("__annotations__", {})
        defaults: dict[str, Any] = {}

        for name, ann in hints.items():
            existing = vars(cls).get(name)
            origin = get_origin(ann)

            # Harvest plain default before overwriting with a descriptor.
            if existing is not None and not is_descriptor(existing):
                defaults[name] = existing

            # Install descriptor if not already one.
            if name not in vars(cls) or not is_descriptor(vars(cls).get(name)):
                if origin is XMLSubElement or origin is XMLAttribute:
                    inst = origin()
                elif origin is XMLElementCollection or ann is XMLElementCollection:
                    inst = XMLElementCollection()
                elif origin is XMLSiblingCollection or ann is XMLSiblingCollection:
                    inst = XMLSiblingCollection()
                else:
                    continue
                inst.__set_name__(cls, name)
                setattr(cls, name, inst)

        cls.__xml_defaults__ = defaults

        if hasattr(cls, "__init__") and hints:
            cls.__init__ = _make_init(hints)

    @property
    def tag(self) -> str:
        return (
            type(self).__name__.lower() if self.__lower_tag__ else type(self).__name__
        )
