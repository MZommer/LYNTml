import logging
import os
import shutil
from pathlib import Path

from core.logger import logger
from lyn.binary_unpacker import Unpacker
from lyn.serializers.binary.timeline_serializer import TimelineSerializer
from lyn.table_reader import table_reader
from lyn.timeline.timeline import JustDanceToolLD

logger.setLevel(logging.ERROR)


def unpack_and_decode(file: os.PathLike) -> JustDanceToolLD:
    unpacker = Unpacker.from_path(file)
    _table, song_table, *files = unpacker.files
    _classifiers_ids, timeline_id = table_reader(song_table.data)

    timeline_file = next(file for file in files if file.id == timeline_id)

    serializer = TimelineSerializer()
    return serializer.deserialize(timeline_file.data)


def main() -> None:
    input_dir = Path("input")
    output_dir = Path("output")
    error_dir = Path("error")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)
    error_dir.mkdir(exist_ok=True)

    for file in input_dir.iterdir():
        if not file.is_file():
            continue
        try:
            timeline = unpack_and_decode(file)
            shutil.copy(
                file, output_dir / f"({timeline.partition.general.Song}){file.name}"
            )
            logger.info("Found %a %a", timeline.partition.general.Song, file.name)
        except Exception:
            shutil.copy(file, error_dir / file.name)


if __name__ == "__main__":
    main()
