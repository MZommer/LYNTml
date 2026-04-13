from io import BytesIO

from core.serializers.binary import BinaryReader, ByteOrder


def table_reader(data: bytes) -> tuple[tuple[int, ...], int]:
    """Reads the table and returns the FileIDs of the classifiers and the timeline."""
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

    classifiers = tuple(binary_reader.uint32() for _ in range(binary_reader.uint32()))
    timeline = binary_reader.uint32()

    return classifiers, timeline
