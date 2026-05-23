from collections.abc import Iterator
from dataclasses import dataclass

from .utils import to_str


@dataclass(slots=True, frozen=True)
class SubElement[T]:
    tag: str
    value: T
    dtype: type[T]

    @property
    def text(self) -> str:
        return to_str(self.value, self.dtype)


@dataclass(slots=True, frozen=True)
class Attribute[T]:
    key: str
    value: T
    dtype: type[T]

    @property
    def text(self) -> str:
        return to_str(self.value, self.dtype)


class CollectionValue[T]:
    def __init__(self, item_type: type[T] | None) -> None:
        self._item_type = item_type
        self._items: list[T] = []

    def _check_type(self, item: object) -> None:
        if self._item_type and not isinstance(item, self._item_type):
            msg = (
                f"Collection expects {self._item_type.__name__}, "
                f"got {type(item).__name__}"
            )
            raise TypeError(msg)

    def append(self, item: T) -> None:
        self._check_type(item)
        self._items.append(item)

    def extend(self, items: list[T]) -> None:
        for item in items:
            self.append(item)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, i: int) -> T:
        return self._items[i]

    def __repr__(self) -> str:
        return f"<Collection({len(self._items)} items)>"
