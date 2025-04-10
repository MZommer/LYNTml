import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, BinaryIO

from .BinaryReader import BinaryReader
from .Logger import logger


@dataclass(frozen=True, slots=True)
class FileID:
    id: int

    def __str__(self) -> str:
        return f"{self.id:x}"

    def __repr__(self):
        return f"FileID({self})"

    def __int__(self):
        return self.id


@dataclass(slots=True)
class File:
    id: FileID
    size: int
    data: bytes
    type: str = "bin"

    def __init__(self, id: int, size: int, data: bytes) -> None:
        self.id = FileID(id)
        self.size = size
        self.data = data
        self._resolve_type()

    def _resolve_type(self):
        if b"\xDE\xC0\xDE\xC0" in self.data:
            self.type = "wog"
        elif b"\xEF\xC0\xDE\xC0" in self.data:
            self.type = "mat"
        elif b"AiLive" in self.data:
            # Live Move Classifier
            self.type = "lmc"
        elif b"Gesture" in self.data:
            self.type = "gesture"
        elif b'<?xml version="1.0" ?>' in self.data:
            self.type = "xml"
        elif b"RIFF" in self.data:
            self.type = "wav"
        else:
            self.type = "bin"
        # TODO: Identify other datatypes    

    def __repr__(self) -> str:
        return f"File(ID={self.id}, Type={self.type} Size={self.size}, Data=bytes[{len(self.data)}])"


class Unpacker:
    files: List[File]

    def __init__(self, file_path: Optional[os.PathLike] = None, stream: Optional[BinaryIO] = None) -> None:
        self.files = []
        if file_path:
            stream = open(file_path, "rb")
        if stream:
            self.from_stream(stream)
        else:
            raise ValueError("Either 'file_path' or 'stream' must be provided.")

    def from_stream(self, stream: BinaryIO) -> None:
        reader = BinaryReader("LITTLE", stream)

        while reader:
            file_id = reader.uint32()
            if file_id == 0xDEAFBEEF:  # b"\xEF\xBE\xAF\xDE" LE
                # Old versions of the engine have this flag for identifying a file
                file_id = reader.uint32()
            file_size = reader.uint32()
            file_data = reader.raw(file_size)
            self.files.append(File(file_id, file_size, file_data))
            # TODO: update to a pointer system to avoid memory flood
            # But also involves in updating the API

    def save_all(self, path: str) -> None:
        base_path = Path(path)
        base_path.mkdir(parents=True, exist_ok=True)  # ensure folder exists
        for idx, file in enumerate(self.files):
            filename = f"{idx} {file.id}.{file.type}"
            self.save_file(file, base_path / filename)

    @staticmethod
    def save_file(file: File, path: os.PathLike) -> None:
        logger.debug(f"Saving file {file.id}.{file.type}")
        with open(path, "wb") as f:
            f.write(file.data)
