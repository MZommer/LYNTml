from io import BytesIO

from core.serializers.binary import BinaryReader, ByteOrder

from .binary_unpacker import FileID


def table_reader(data: bytes) -> tuple[tuple[FileID, ...], FileID]:
    binary_reader = BinaryReader(ByteOrder.LITTLE, BytesIO(data))

    _size_of = binary_reader.uint32()

    unk0 = binary_reader.uint32()
    if unk0 != 8197:
        msg = "Unexpected value for unk0"
        raise Exception(msg)
    unk1 = binary_reader.uint32()
    if unk1 != 4294901761:
        msg = "Unexpected value for unk1"
        raise Exception(msg)
    unk2 = binary_reader.uint32()
    if unk2 != 77:
        msg = "Unexpected value for unk2"
        raise Exception(msg)
    # I think this are all int16 values

    _files = binary_reader.ushort()

    classifiers = tuple(
        FileID(binary_reader.uint32()) for _ in range(binary_reader.uint32())
    )
    timeline = FileID(binary_reader.uint32())

    return classifiers, timeline
