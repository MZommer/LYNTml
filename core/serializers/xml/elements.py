from abc import ABC
from typing import Any, get_origin

from .descriptors import (
    XMLAttribute,
    XMLElementCollection,
    XMLSiblingCollection,
    XMLSubElement,
)
from .utils import all_hints, is_descriptor


def _make_init(
    hints: dict,
    defaults: dict,
    disc_field: str | None = None,
    disc_value: str | None = None,
) -> callable:
    """Generate __init__ from schema annotations.

    Ordering (mirrors dataclass):
      1. Required fields (no default) — XMLSubElement / XMLAttribute only.
      2. Optional fields — those with defaults, plus all collections
         (XMLElementCollection and XMLSiblingCollection).

    All assignments route through descriptors -> type-checking is free.
    """
    is_collection = lambda ann: (
        get_origin(ann) in (XMLElementCollection, XMLSiblingCollection)
        or ann in (XMLElementCollection, XMLSiblingCollection)
    )

    required = [
        (n, a)
        for n, a in hints.items()
        if n not in defaults and not is_collection(a) and n != disc_field
    ]
    optional = [
        (n, a)
        for n, a in hints.items()
        if (n in defaults or is_collection(a)) and n != disc_field
    ]

    params = ["self"]
    body_lines = []

    # Auto-fill the discriminator field without exposing it as a parameter
    if disc_field and disc_value is not None:
        body_lines.append(f"    self.{disc_field} = __defs__['__disc__']")

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

    ns: dict = {"__defs__": {**defaults, "__disc__": disc_value}}
    exec(src, ns)  # noqa: S102
    return ns["__init__"]


class XMLElement(ABC):
    """Base for all XML-mapped elements.

    Subclasses get:
      • Descriptor instances auto-installed for every annotated field.
      • Default values harvested from the class body.
      • A type-checked __init__ auto-generated from the schema.

    Polymorphic collections
    -----------------------
    Declare a discriminator on the base class and a discriminator_value on
    each subclass. The serializer reads/writes the correct subtype automatically:

        class Layer(XMLElement, discriminator="type"):
            name:     XMLAttribute[str]
            type:     XMLAttribute[str]
            position: XMLAttribute[int]

        class MoveLayer(Layer, discriminator_value="Move"):
            move_data: XMLSubElement[str]   # extra fields on this subtype

        class EventsLayer(Layer, discriminator_value="Events"):
            event_count: XMLSubElement[int]

        class partition(XMLElement):
            Layers: XMLSiblingCollection[Layer]  # typed as base; dispatches to subtypes

    All subtypes share the base's XML tag name and inherit its fields.
    """

    # Polymorphic dispatch — populated by __init_subclass__
    _discriminator_attr: str | None = None  # which XML attr holds the type key
    _discriminator_registry: dict = {}  # {value -> subclass}
    _discriminator_root: type | None = None  # the class that owns the registry

    def __init_subclass__(
        cls,
        discriminator: str | None = None,
        discriminator_value: str | None = None,
        **kwargs,
    ) -> None:
        super().__init_subclass__(**kwargs)

        # ---- polymorphic registry ------------------------------------------
        if discriminator is not None:
            # This class is the polymorphic root.
            cls._discriminator_attr = discriminator
            cls._discriminator_registry = {}
            cls._discriminator_root = cls

        if discriminator_value is not None:
            # Find nearest ancestor that owns a registry.
            root = next(
                (
                    b
                    for b in cls.__mro__[1:]
                    if getattr(b, "_discriminator_root", None) is b
                ),
                None,
            )
            if root is None:
                raise TypeError(
                    f"{cls.__name__}: discriminator_value given but no discriminator "
                    f"root found in MRO — did you forget discriminator='...' on the base?"
                )
            root._discriminator_registry[discriminator_value] = cls
            cls._discriminator_value = discriminator_value

        # ---- descriptor installation ---------------------------------------
        # Only install descriptors for fields declared on THIS class, not inherited ones.
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
                if origin is XMLSubElement:
                    inst = XMLSubElement()
                    inst.__set_name__(cls, name)
                    setattr(cls, name, inst)
                elif origin is XMLAttribute:
                    inst = XMLAttribute()
                    inst.__set_name__(cls, name)
                    setattr(cls, name, inst)
                elif origin is XMLElementCollection or ann is XMLElementCollection:
                    inst = XMLElementCollection()
                    inst.__set_name__(cls, name)
                    setattr(cls, name, inst)
                elif origin is XMLSiblingCollection or ann is XMLSiblingCollection:
                    inst = XMLSiblingCollection()
                    inst.__set_name__(cls, name)
                    setattr(cls, name, inst)

        cls.__xml_defaults__ = defaults

        # Auto-generate __init__ only when not explicitly defined AND when
        # there are any annotations across the whole MRO to work with.
        if "__init__" not in vars(cls) and all_hints(cls):
            disc_field = getattr(cls, "_discriminator_attr", None)
            disc_value = getattr(cls, "_discriminator_value", None)
            # Suppress discriminator field from params only for registered subtypes,
            # not for the root itself.
            if disc_value is None or getattr(cls, "_discriminator_root", None) is cls:
                disc_field = None
            cls.__init__ = _make_init(all_hints(cls), defaults, disc_field, disc_value)

    @property
    def tag(self) -> str:
        # Subtypes registered under a discriminator root emit the ROOT's tag,
        # so <Layer .../> is always the element name regardless of MoveLayer vs EventsLayer.
        root = getattr(type(self), "_discriminator_root", None)
        return root.__name__ if root else type(self).__name__
