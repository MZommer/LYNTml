from __future__ import annotations

from typing import Any, Self, get_args, overload

from .utils import all_hints, type_arg, typecheck
from .wrappers import Attribute, CollectionValue, SubElement


class XMLSubElement[T]:
    """Child element: <Tag>value</Tag>."""

    def __set_name__(self, _owner: type[Any], name: str) -> None:
        self._field = name
        self._slot = f"__sub_{name}"

    # Overload 1: When accessed from the class (e.g., MyClass.field -> returns the descriptor)
    @overload
    def __get__(self, obj: None, objtype: type | None = None) -> Self: ...

    # Overload 2: When accessed from an instance (e.g., my_instance.field -> returns T)
    @overload
    def __get__[Instance](
        self, obj: Instance, objtype: type[Instance] | None = None
    ) -> T: ...

    def __get__[Instance](
        self, obj: Instance | None, objtype: type[Instance] | None = None
    ) -> Self | T:
        if obj is None:
            return self

        wrapper: SubElement[T] | None = obj.__dict__.get(self._slot)
        if wrapper is None:
            msg = f"'{objtype.__name__}.{self._field}' has not been set."
            raise AttributeError(msg)
        return wrapper.value

    def __set__[Instance](self, obj: Instance, value: T) -> None:
        dtype = type_arg(all_hints(type(obj))[self._field])
        typecheck(value, dtype, field=f"{type(obj).__name__}.{self._field}")
        obj.__dict__[self._slot] = SubElement(self._field, value, dtype)


class XMLAttribute[T]:
    """Tag attribute: <Tag key="value" />."""

    def __set_name__(self, _owner: type[Any], name: str) -> None:
        self._field = name
        self._slot = f"__attr_{name}"

    @overload
    def __get__(self, obj: None, objtype: type[Any] | None = None) -> Self: ...

    @overload
    def __get__[Instance](
        self, obj: Instance, objtype: type[Instance] | None = None
    ) -> T: ...

    def __get__[Instance](
        self, obj: Instance | None, objtype: type[Instance] | None = None
    ) -> Self | T:
        if obj is None:
            return self
        wrapper: Attribute[T] | None = obj.__dict__.get(self._slot)
        if wrapper is None:
            msg = f"'{objtype.__name__}.{self._field}' has not been set."
            raise AttributeError(msg)
        return wrapper.value

    def __set__[Instance](self, obj: Instance, value: T) -> None:
        dtype = type_arg(all_hints(type(obj))[self._field])
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

    def __set_name__(self, _owner: type[Any], name: str) -> None:
        self._field = name
        self._slot = f"__col_{name}"

    def _item_type(self, owner: type[Any]) -> type[T] | None:
        ann = vars(owner)["__annotations__"].get(self._field)
        return type_arg(ann) if ann and get_args(ann) else None

    @overload
    def __get__(self, obj: None, objtype: type[Any] | None = None) -> Self: ...

    @overload
    def __get__[Instance](
        self, obj: Instance, objtype: type[Instance] | None = None
    ) -> CollectionValue[T]: ...

    def __get__[Instance](
        self, obj: Instance | None, objtype: type[Instance] | None = None
    ) -> Self | CollectionValue[T]:
        if obj is None:
            return self

        value: CollectionValue[T] | None = obj.__dict__.get(self._slot)
        if value is None:
            value = CollectionValue(item_type=self._item_type(type(obj)))
            obj.__dict__[self._slot] = value
        return value

    def __set__[Instance](self, _obj: Instance, _value: T) -> None:
        msg = (
            f"Use {self._field}.append() / .extend()"
            " — direct assignment is not allowed."
        )
        raise AttributeError(msg)


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

    def __set_name__(self, _owner: type[Any], name: str) -> None:
        self._field = name
        self._slot = f"__sib_{name}"

    def _item_type(self, owner: type[Any]) -> type[T] | None:
        ann = vars(owner)["__annotations__"].get(self._field)
        return type_arg(ann) if ann and get_args(ann) else None

    @overload
    def __get__(self, obj: None, objtype: type[Any] | None = None) -> Self: ...

    @overload
    def __get__[Instance](
        self, obj: Instance, objtype: type[Instance] | None = None
    ) -> CollectionValue[T]: ...

    def __get__[Instance](
        self, obj: Instance | None, objtype: type[Instance] | None = None
    ) -> Self | CollectionValue[T]:
        if obj is None:
            return self

        value: CollectionValue[T] | None = obj.__dict__.get(self._slot)
        if value is None:
            value = CollectionValue(item_type=self._item_type(type(obj)))
            obj.__dict__[self._slot] = value
        return value

    def __set__[Instance](self, _obj: Instance, _value: T) -> None:
        msg = (
            f"Use {self._field}.append() / .extend()"
            " — direct assignment is not allowed."
        )
        raise AttributeError(msg)
