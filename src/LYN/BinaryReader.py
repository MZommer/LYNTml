import struct
from dataclasses import dataclass
from queue import LifoQueue
from typing import Literal, BinaryIO, Optional, Callable, List, Union


@dataclass
class StructInfo:
    seed: int
    size_of: int


class BinaryReader:
    def __init__(self, endianess: Literal["BIG", "LITTLE"], file_stream: BinaryIO):
        self.stack = LifoQueue()
        self.endianess_marker = "<"
        if endianess == "BIG":
            self.endianess_marker = ">"
        self.endianess = endianess
        self.file_stream = file_stream

    def init_struct(self):
        seed = self.tell()
        size_of = self.uint32()
        info = self.put_struct(seed, size_of)
        return info

    def put_struct(self, seed: int, size_of: int) -> StructInfo:
        info = StructInfo(seed, size_of)
        self.stack.put(info)
        return info

    def get_struct(self):
        return self.stack.get()

    def vector(self, size: Optional[int] = None) -> List[float]:
        return [self.float() for _ in range(size or self.uint32())]

    def array(self, function: Callable) -> List:
        return [function() for _ in range(self.uint32())]

    def uint64(self) -> int:
        return struct.unpack(self.endianess_marker + "Q", self.file_stream.read(8))[0]

    def int64(self) -> int:
        return struct.unpack(self.endianess_marker + "q", self.file_stream.read(8))[0]

    def uint32(self) -> int:
        return struct.unpack(self.endianess_marker + "I", self.file_stream.read(4))[0]

    def int32(self) -> int:
        return struct.unpack(self.endianess_marker + "i", self.file_stream.read(4))[0]

    def ushort(self) -> int:
        return struct.unpack(self.endianess_marker + "H", self.file_stream.read(2))[0]

    def short(self) -> int:
        return struct.unpack(self.endianess_marker + "h", self.file_stream.read(2))[0]

    def ubyte(self) -> int:
        return struct.unpack(self.endianess_marker + "B", self.file_stream.read(1))[0]

    def byte(self) -> int:
        return struct.unpack(self.endianess_marker + "b", self.file_stream.read(1))[0]

    def bool(self) -> bool:
        return struct.unpack(self.endianess_marker + "?", self.file_stream.read(1))[0]

    def float(self, do_round=True) -> Union[float, int]:
        value = struct.unpack(self.endianess_marker + "f", self.file_stream.read(4))[0]
        if do_round:
            value = round(value, 7)
        if (value % 1) == 0:
            value = int(value)
        return value

    def string4(self) -> str:
        return self.file_stream.read(self.ushort()).strip(b"\x00").decode("utf-8")

    def string(self, is_lyn=False) -> str:
        if not is_lyn:
            return self.file_stream.read(self.uint32()).strip(b"\x00").decode("utf-8")
        size = self.ushort()
        is_unicode = self.ushort()
        if is_unicode:
            string = self.file_stream.read(size).rstrip(b"\x00").decode("utf-16", "backslashreplace")
            arr = string.split(r"\x")
            for index, i in enumerate(arr):
                if index == 0:
                    continue
                arr[index] = bytearray.fromhex(i[:2]).decode() + i[2:]
            return "".join(arr)
        return self.file_stream.read(size).replace(b"\x00", b"").decode("utf-8")

    def raw(self, size) -> bytes:
        return self.file_stream.read(size)

    def tell(self) -> int:
        return self.file_stream.tell()

    def seek(self, offset: int, whence: int = 0):
        self.file_stream.seek(offset, whence)

    def close(self):
        self.file_stream.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __repr__(self) -> str:
        return f"BinaryReader(endianess={self.endianess}, ptr={self.tell()})"

    def __bool__(self) -> bool:
        byte = self.file_stream.read(1)
        self.file_stream.seek(-1, 1)
        return bool(byte)
