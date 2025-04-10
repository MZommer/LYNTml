from typing import Tuple
from io import BytesIO

from .BinaryReader import BinaryReader
from .BinaryUnpacker import FileID


def TableReader(data: bytes) -> Tuple[Tuple[FileID, ...], FileID]:
    binary_reader = BinaryReader("LITTLE", BytesIO(data))

    size_of = binary_reader.uint32()

    unk0 = binary_reader.uint32()
    if unk0 != 8197:
        raise Exception("Unexpected value for unk0")
    unk1 = binary_reader.uint32()
    if unk1 != 4294901761:
        raise Exception("Unexpected value for unk1")
    unk2 = binary_reader.uint32()
    if unk2 != 77:
        raise Exception("Unexpected value for unk2")

    files = binary_reader.ushort()

    classifiers = tuple(FileID(binary_reader.uint32()) for _ in range(binary_reader.uint32()))
    timeline = FileID(binary_reader.uint32())

    return classifiers, timeline
