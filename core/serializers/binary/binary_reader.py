import struct
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from queue import LifoQueue
from typing import BinaryIO


@dataclass
class StructInfo:
    seed: int
    size_of: int


class ByteOrder(StrEnum):
    BIG = "BIG"
    LITTLE = "LITTLE"


class BinaryReader:
    def __init__(self, byte_order: ByteOrder, file_stream: BinaryIO) -> None:
        self.stack: LifoQueue[object] = LifoQueue()
        self.byte_order_marker = "<" if byte_order == ByteOrder.LITTLE else ">"
        self.byte_order = ByteOrder
        self.file_stream = file_stream

    def init_struct(self):
        seed = self.tell()
        size_of = self.uint32()
        return self.put_struct(seed, size_of)

    def put_struct(self, seed: int, size_of: int) -> StructInfo:
        info = StructInfo(seed, size_of)
        self.stack.put(info)
        return info

    def get_struct(self):
        return self.stack.get()

    def vector(self, size: int | None = None) -> list[float]:
        return [self.float() for _ in range(size or self.uint32())]

    def array[T](self, function: Callable[[], T]) -> list[T]:
        return [function() for _ in range(self.uint32())]

    def uint64(self) -> int:
        return struct.unpack(self.byte_order_marker + "Q", self.file_stream.read(8))[0]

    def int64(self) -> int:
        return struct.unpack(self.byte_order_marker + "q", self.file_stream.read(8))[0]

    def uint32(self) -> int:
        return struct.unpack(self.byte_order_marker + "I", self.file_stream.read(4))[0]

    def int32(self) -> int:
        return struct.unpack(self.byte_order_marker + "i", self.file_stream.read(4))[0]

    def ushort(self) -> int:
        return struct.unpack(self.byte_order_marker + "H", self.file_stream.read(2))[0]

    def short(self) -> int:
        return struct.unpack(self.byte_order_marker + "h", self.file_stream.read(2))[0]

    def ubyte(self) -> int:
        return struct.unpack(self.byte_order_marker + "B", self.file_stream.read(1))[0]

    def byte(self) -> int:
        return struct.unpack(self.byte_order_marker + "b", self.file_stream.read(1))[0]

    def bool(self) -> bool:
        return struct.unpack(self.byte_order_marker + "?", self.file_stream.read(1))[0]

    def float(self, round_value: bool = True) -> float:
        value = struct.unpack(self.byte_order_marker + "f", self.file_stream.read(4))[0]
        if round_value:
            value = round(value, 7)
        return value

    def string4(self) -> str:
        return self.file_stream.read(self.ushort()).strip(b"\x00").decode("utf-8")

    def string8(self) -> str:
        return self.file_stream.read(self.uint32()).strip(b"\x00").decode("utf-8")

    def string16(self) -> str:
        size = self.ushort()
        is_utf16 = self.ushort()
        if is_utf16:
            string = (
                self.file_stream.read(size)
                .rstrip(b"\x00")
                .decode("utf-16", "backslashreplace")
            )
            # Try to decode errors in utf-8
            errors = string.split(r"\x")
            for index, chunk in enumerate(errors):
                if index == 0:
                    continue
                errors[index] = bytearray.fromhex(chunk[:2]).decode("utf-8") + chunk[2:]
            return "".join(errors)
        return self.file_stream.read(size).replace(b"\x00", b"").decode("utf-8")

    def date(self) -> datetime:
        return datetime(
            year=self.ushort(),
            month=self.ushort(),
            day=self.ushort(),
            minute=self.ushort(),
            hour=self.ushort(),
            second=self.ushort(),
            microsecond=self.uint32(),
        )

    def raw(self, size: int) -> bytes:
        return self.file_stream.read(size)

    def tell(self) -> int:
        return self.file_stream.tell()

    def seek(self, offset: int, whence: int = 0) -> None:
        self.file_stream.seek(offset, whence)

    def close(self) -> None:
        self.file_stream.close()

    def __del__(self) -> None:
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __repr__(self) -> str:
        return f"BinaryReader(byte_order={self.byte_order}, ptr={self.tell()})"

    def __bool__(self) -> bool:
        byte = self.file_stream.read(1)
        self.file_stream.seek(-1, 1)
        return bool(byte)
