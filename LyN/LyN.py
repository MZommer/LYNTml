import os
from pathlib import Path

from .binary_unpacker import Unpacker
from .logger import logger
from .table_reader import table_reader
from .Timeline.BinarySerializer import BinarySerializer
from .Timeline.timeline import Timeline


class LyN:
    @staticmethod
    def UnpackAndDecode(file: os.PathLike, output: os.PathLike) -> Timeline:
        output = Path(output)
        unpacker = Unpacker(file)

        _header, table, *files = unpacker.files

        os.makedirs(output / "bin", exist_ok=True)
        for idx, file in enumerate(unpacker.files):
            unpacker.save_file(file, output / "bin" / f"{idx}_{file.id}.{file.type}")

        classifiers_id, timeline_id = table_reader(table.data)

        classifiers = tuple(file for file in files if file.id in classifiers_id)
        timeline_file = next(file for file in files if file.id == timeline_id)

        serializer = BinarySerializer()
        timeline = serializer.deserialize(timeline_file.data)

        timeline.write(output / f"{timeline.general.Song}.tml")
        os.makedirs(output / "classifiers", exist_ok=True)

        for move in timeline.databank.MoveBank:
            try:
                classifier = classifiers[move.CreationId]
            except IndexError:
                logger.exception(f"Missing classifier {move.name}")
            classifier_path = os.path.join(
                output,
                "classifiers",
                f"{move.name}_{timeline.general.Song}.{classifier.type}".lower(),
            )
            with open(classifier_path, "wb") as f:
                f.write(classifier.data)

        return timeline
