from io import BytesIO

from core.serializers.binary import BinaryReader, ByteOrder


def table_reader(data: bytes) -> tuple[tuple[int, ...], int]:
    """Reads the table and returns the FileIDs of the classifiers and the timeline."""
    binary_reader = BinaryReader(ByteOrder.LITTLE, BytesIO(data))

    _size_of = binary_reader.uint32()

    unk0 = binary_reader.uint32()
    assert unk0 == 8197, "Unexpected value for unk0"
    unk1 = binary_reader.uint32()
    assert unk1 == 4294901761, "Unexpected value for unk1"
    unk2 = binary_reader.uint32()
    assert unk2 == 77, "Unexpected value for unk2"
    # I think this are all int16 values

    _files = binary_reader.ushort()

    classifiers = tuple(binary_reader.uint32() for _ in range(binary_reader.uint32()))
    timeline = binary_reader.uint32()

    return classifiers, timeline
