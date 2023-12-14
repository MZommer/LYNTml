from .BinaryReader import BinaryReader
from .BinaryUnpacker import FileID
from io import BytesIO

def TableReader(data: bytes) -> tuple[tuple[FileID], FileID]:
    binaryReader = BinaryReader("LITTLE", BytesIO(data))
    
    sizeOf = binaryReader.uint32()
    
    unk0 = binaryReader.uint32()
    if unk0 != 8197:
        raise Exception("Unexpected value for unk0")
    unk1 = binaryReader.uint32()
    if unk1 != 4294901761:
        raise Exception("Unexpected value for unk1")
    unk2 = binaryReader.uint32()
    if unk2 != 77:
        raise Exception("Unexpected value for unk2")
    
    files = binaryReader.ushort()
    
    classifiers = tuple(FileID(binaryReader.uint32()) for _ in range(binaryReader.uint32()))
    timeline = FileID(binaryReader.uint32())
    
    return classifiers, timeline
