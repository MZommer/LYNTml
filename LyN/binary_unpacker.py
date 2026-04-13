from __future__ import annotations

import os
from collections.abc import Iterator, Sequence
from enum import StrEnum
from pathlib import Path
from typing import BinaryIO

from core.logger import logger
from core.serializers.binary import BinaryReader, ByteOrder


class FileType(StrEnum):
    """Known file-type signatures detected from raw bytes."""

    WOG = "wog"
    MAT = "mat"
    LMC = "lmc"  # Live Move Classifier
    GESTURE = "gesture"
    XML = "xml"
    WAV = "wav"
    UNKNOWN = "bin"


# Magic signatures in detection-priority order.
# Each entry: (bytes_to_search, FileType)
_SIGNATURES: tuple[tuple[bytes, FileType], ...] = (
    (b"\xde\xc0\xde\xc0", FileType.WOG),
    (b"\xef\xc0\xde\xc0", FileType.MAT),
    (b"AiLive", FileType.LMC),
    (b"Gesture", FileType.GESTURE),
    (b'<?xml version="1.0" ?>', FileType.XML),
    (b"RIFF", FileType.WAV),
)


def detect_type(data: bytes) -> FileType:
    """Detect the file type from raw bytes using magic signatures."""
    for signature, file_type in _SIGNATURES:
        if signature in data:
            return file_type
    return FileType.UNKNOWN


class File:
    """Immutable representation of a single packed file.

    Attributes
    ----------
    id   : unique numeric identifier from the archive (displayed as hex)
    data : raw bytes
    type : detected FileType

    """

    __slots__ = ("_data", "_id", "_type")

    def __init__(self, file_id: int, data: bytes) -> None:
        self._id: int = file_id
        self._data: bytes = data
        self._type: FileType = detect_type(data)

    @property
    def id(self) -> int:
        return self._id

    @property
    def data(self) -> bytes:
        return self._data

    @property
    def size(self) -> int:
        """Byte length of the payload — always consistent with data."""
        return len(self._data)

    @property
    def type(self) -> FileType:
        return self._type

    def __str__(self) -> str:
        return f"{self._id:x}.{self._type}  ({self.size} bytes)"

    def __repr__(self) -> str:
        return f"File(id=0x{self._id:x}, type={self._type!r}, size={self.size})"


_LEGACY_HEADER: int = 0xDEAFBEEF  # old-engine sentinel word


class Unpacker:
    """Parses a binary archive stream into a list of File objects.

    Usage
    -----
    # From a file path (context-manager handled internally):
    unpacker = Unpacker.from_path("archive.bin")

    # From an already-open stream:
    with open("archive.bin", "rb") as f:
        unpacker = Unpacker.from_stream(f)

    files: tuple[File] = unpacker.files
    """

    def __init__(self, files: Sequence[File]) -> None:
        self._files = tuple(files)

    @property
    def files(self) -> tuple[File, ...]:
        return self._files

    def __len__(self) -> int:
        return len(self._files)

    def __iter__(self) -> Iterator[File]:
        return iter(self._files)

    def __repr__(self) -> str:
        return f"Unpacker({len(self._files)} files)"

    @classmethod
    def from_path(cls, path: os.PathLike | str) -> Unpacker:
        """Open *path*, parse the archive, close the file — always."""
        with open(path, "rb") as stream:
            return cls.from_stream(stream)

    @classmethod
    def from_stream(cls, stream: BinaryIO) -> Unpacker:
        """Parse an archive from an already-open binary stream."""
        return cls(tuple(cls._parse(stream)))

    @staticmethod
    def _parse(stream: BinaryIO) -> Iterator[File]:
        """Yield File objects by reading (id, size, data) triplets.

        The legacy header word 0xDEAFBEEF is transparently skipped so
        both old-engine and new-engine archives are handled identically.
        """
        reader = BinaryReader(ByteOrder.LITTLE, stream)

        while reader:
            file_id = reader.uint32()

            if file_id == _LEGACY_HEADER:
                file_id = reader.uint32()  # real id follows the sentinel

            file_size = reader.uint32()
            file_data = reader.raw(file_size)

            yield File(file_id, file_data)


def save_all(
    files: list[File],
    dest: os.PathLike | str,
    *,
    overwrite: bool = True,
) -> list[Path]:
    """Write every file to *dest*, returning the paths actually written.

    Filename format: ``<hex-id>.<type>``  e.g. ``1a2b3c.xml``
    The FileID is unique within an archive, so no index prefix is needed.

    Parameters
    ----------
    files     : files to write (any iterable)
    dest      : target directory (created if absent)
    overwrite : when False, existing files are skipped with a warning

    """
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    for file in files:
        path = dest / f"{file.id:x}.{file.type}"

        if path.exists() and not overwrite:
            logger.warning(f"Skipping {path.name} — file already exists")
            continue

        logger.debug(f"Writing {path.name}  ({file.size} bytes)")
        path.write_bytes(file.data)
        written.append(path)

    return written


def save_file(file: File, path: os.PathLike | str) -> Path:
    """Write a single file to an explicit path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Writing {path}  ({file.size} bytes)")
    path.write_bytes(file.data)
    return path
