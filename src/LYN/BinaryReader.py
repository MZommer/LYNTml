import struct
from queue import LifoQueue
from dataclasses import dataclass
from .Logger import logger

@dataclass
class StructInfo:
   seed: int
   sizeOf: int 

class BinaryReader:
    def __init__(self, endianess, fileStream):
        self.stack = LifoQueue()
        self.parameterMarker = "<"
        if endianess == "BIG":
            self.parameterMarker = ">"
        self.endianess = endianess
        self.fileStream = fileStream
    
    def InitStruct(self):
        seed = self.tell()
        sizeOf = self.uint32()
        info = self.PutStruct(seed, sizeOf)
        return info
    
    def PutStruct(self, seed, sizeOf):
        info = StructInfo(seed, sizeOf)
        self.stack.put(info)
        return info
    
    def GetStruct(self):
        return self.stack.get()
    
    def vector(self, len=None):
        return [self.float() for _ in range(len or self.uint32())]

    def array(self, function):
        return [function() for _ in range(self.uint32())]

    def uint64(self):
        return struct.unpack(self.parameterMarker + "Q", self.fileStream.read(8))[0]

    def int64(self):
        return struct.unpack(self.parameterMarker + "q", self.fileStream.read(8))[0]

    def uint32(self):
        return struct.unpack(self.parameterMarker + "I", self.fileStream.read(4))[0]

    def int32(self):
        return struct.unpack(self.parameterMarker + "i", self.fileStream.read(4))[0]

    def ushort(self):
        return struct.unpack(self.parameterMarker + "H", self.fileStream.read(2))[0]

    def short(self):
        return struct.unpack(self.parameterMarker + "h", self.fileStream.read(2))[0]

    def ubyte(self):
        return struct.unpack(self.parameterMarker + "B", self.fileStream.read(1))[0]

    def byte(self):
        return struct.unpack(self.parameterMarker + "b", self.fileStream.read(1))[0]

    def bool(self):
        return struct.unpack(self.parameterMarker + "?", self.fileStream.read(1))[0]

    def float(self, doRound=True):
        value = struct.unpack(self.parameterMarker + "f", self.fileStream.read(4))[0]
        if doRound:
            value = round(value, 7)
        if (value % 1) == 0:
            value = int(value)
        return value

    def string4(self):
        return self.fileStream.read(self.ushort()).strip(b"\x00").decode("utf-8")

    def string(self, isLYN=False):
        if not isLYN:
            return self.fileStream.read(self.uint32()).strip(b"\x00").decode("utf-8")
        size = self.ushort()
        isUnicode = self.ushort()
        if isUnicode:
            string = self.fileStream.read(size).rstrip(b"\x00").decode("utf-16", "backslashreplace")
            arr = string.split(r"\x")
            for index, i in enumerate(arr):
                if index == 0:
                    continue
                arr[index] = bytearray.fromhex(i[:2]).decode() + i[2:]
            return "".join(arr)
        return self.fileStream.read(size).replace(b"\x00", b"").decode("utf-8")
    
    def raw(self, size):
        return self.fileStream.read(size)
    
    def tell(self):
        return self.fileStream.tell()
    
    def seek(self, *args, **kwargs):
        self.fileStream.seek(*args, **kwargs)
    
    def close(self):
        self.fileStream.close()
    
    def __del__(self):
        self.close()
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def __repr__(self):
        return f"BinaryReader(endianess={self.endianess}, pptr={self.tell()})"
