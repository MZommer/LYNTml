from dataclasses import dataclass
from .BinaryReader import BinaryReader
from io import BytesIO
import struct
import binascii

# make a function that returns the size of the buffer
def getBufferSize(f: BytesIO) -> int:
    pos = f.tell()
    f.seek(0, 2)
    size = f.tell()
    f.seek(pos)
    return size

@dataclass(frozen=True, slots=True)
class FileID:
    ID: int
    
    def __str__(self) -> str:
        return binascii.hexlify(struct.pack("<I", self.ID)).decode("utf-8")

@dataclass(slots=True)
class File:
    ID: int
    Size: int
    Data: bytes
    Type: str = "bin"
    
    def __init__(self, ID: int, Size: int, Data: bytes) -> None:
        self.ID = FileID(ID)
        self.Size = Size
        self.Data = Data
        
        if b"\xDE\xC0\xDE\xC0" in self.Data:
            self.Type = "wog"
        elif b"\xEF\xC0\xDE\xC0" in self.Data:
            self.Type = "mat"
        elif b"AiLive" in self.Data:
            # Live Move Classifier
            self.Type = "lmc"
        elif b"Gesture" in self.Data:
            self.Type = "gesture"
        elif b'<?xml version="1.0" ?>' in self.Data:
            self.Type = "xml"
        elif b"RIFF" in self.Data:
            self.Type = "wav"
        else:
            self.Type = "bin"        
    
    def __repr__(self) -> str:
        return f"File(ID={self.ID}, Type={self.Type} Size={self.Size}, Data=bytes[{len(self.Data)}])"


class Unpacker:
    files: list[File]
    
    def __init__(self, file: str = None, stream: BytesIO = None) -> None:
        if file:
            stream = open(file, "rb")
        if stream:
            self.FromStream(stream)
    
    def FromStream(self, stream: BytesIO) -> None:
        binaryReader = BinaryReader("LITTLE", stream)
        self.files = []
        size = getBufferSize(binaryReader.fileStream)
        
        while binaryReader.tell() != size:
            FileID = binaryReader.uint32()
            if FileID == 0xDEAFBEEF: # b"\xEF\xBE\xAF\xDE" LE
                # Old versions of the engine have this flag for identifying a file
                FileID = binaryReader.uint32()
            FileSize = binaryReader.uint32()
            FileData = binaryReader.raw(FileSize)
            self.files.append(File(FileID, FileSize, FileData))
    
    def SaveAll(self, path: str) -> None:
        for idx, file in enumerate(self.files):
            self.SaveFile(file, f"{path}{idx} {file.ID}.{file.Type}")
    
    def SaveFile(self, file: File, path: str) -> None:
        print(file)
        with open(path, "wb") as f:
            f.write(file.Data)