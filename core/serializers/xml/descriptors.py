from typing import get_args

from .utils import type_arg, typecheck
from .wrappers import Attribute, CollectionValue, SubElement


class XMLSubElement[T]:
    """Child element: <Tag>value</Tag>."""

    def __set_name__(self, _owner: type, name: str) -> None:
        self._field = name
        self._slot = f"__sub_{name}"

    def _dtype(self, owner: type) -> type[T]:
        return type_arg(vars(owner)["__annotations__"][self._field])

    def __get__(self, obj, objtype=None) -> SubElement[T]:
        if obj is None:
            return self
        value = obj.__dict__.get(self._slot)
        if value is None:
            msg = f"'{objtype.__name__}.{self._field}' has not been set."
            raise AttributeError(
                msg
            )
        # TODO: Worth checking `value`'s type?
        return value

    def __set__(self, obj, value: T) -> None:
        dtype = self._dtype(type(obj))
        typecheck(value, dtype, field=f"{type(obj).__name__}.{self._field}")
        obj.__dict__[self._slot] = SubElement(self._field, value, dtype)


class XMLAttribute[T]:
    """Tag attribute: <Tag key="value" />."""

    def __set_name__(self, _owner: type, name: str) -> None:
        self._field = name
        self._slot = f"__attr_{name}"

    def _dtype(self, owner: type) -> type[T]:
        return type_arg(vars(owner)["__annotations__"][self._field])

    def __get__(self, obj, objtype=None) -> Attribute[T]:
        if obj is None:
            return self
        value = obj.__dict__.get(self._slot)
        if value is None:
            msg = f"'{objtype.__name__}.{self._field}' has not been set."
            raise AttributeError(
                msg
            )
        return value

    def __set__(self, obj, value: T) -> None:
        dtype = self._dtype(type(obj))
        typecheck(value, dtype, field=f"{type(obj).__name__}.{self._field}")
        obj.__dict__[self._slot] = Attribute(self._field, value, dtype)


class XMLElementCollection[T]:
    """Wrapped collection — children live inside a container tag
    example:
        <ScoreSteps>
            <ScoreStep Name="X" Value="1" />
            <ScoreStep Name="OK" Value="25" />
        </ScoreSteps>.
    """

    def __set_name__(self, _owner: type, name: str) -> None:
        self._field = name
        self._slot = f"__col_{name}"

    def _item_type(self, owner: type) -> type[T] | None:
        ann = vars(owner)["__annotations__"].get(self._field)
        return type_arg(ann) if ann and get_args(ann) else None

    def __get__(self, obj, _objtype=None) -> CollectionValue[T]:
        if obj is None:
            return self
        value = obj.__dict__.get(self._slot)
        if value is None:
            value = CollectionValue(item_type=self._item_type(type(obj)))
            obj.__dict__[self._slot] = value
        return value

    def __set__(self, _obj, _) -> None:
        msg = (
            f"Use {self._field}.append() / .extend()"
            " — direct assignment is not allowed."
        )
        raise AttributeError(
            msg
        )


class XMLSiblingCollection[T]:
    """Unwrapped sibling collection — children are emitted directly at the
    parent level, with no container tag, identified only by their tag name:

        <Layer name="Moves1"     type="Move"   position="0" />
        <Layer name="KinectMoves1" type="Move" position="1" />
        <Layer name="Events_23"  type="Events" position="2" />

    Use this when:
      • The XML repeats the same tag as siblings of other elements.
      • You don't know how many to expect.

    The XML tag searched/emitted is item_type().tag (i.e. the class name by
    default, or whatever .tag returns).
    """

    def __set_name__(self, _owner: type, name: str) -> None:
        self._field = name
        self._slot = f"__sib_{name}"

    def _item_type(self, owner: type) -> type[T] | None:
        ann = vars(owner)["__annotations__"].get(self._field)
        return type_arg(ann) if ann and get_args(ann) else None

    def __get__(self, obj, objtype=None) -> CollectionValue[T]:
        if obj is None:
            return self
        value = obj.__dict__.get(self._slot)
        if value is None:
            value = CollectionValue(item_type=self._item_type(type(obj)))
            obj.__dict__[self._slot] = value
        return value

    def __set__(self, _obj, _) -> None:
        msg = (
            f"Use {self._field}.append() / .extend()"
            " — direct assignment is not allowed."
        )
        raise AttributeError(
            msg
        )
