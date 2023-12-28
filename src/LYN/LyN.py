import os
from os import path
from .BinaryUnpacker import Unpacker
from .TableReader import TableReader
from .Timeline.BinarySerializer import BinarySerializer

class LyN:
    @staticmethod
    def UnpackAndDecode(file: str, output: str) -> None:
        unpacker = Unpacker(file)
        
        header, table, *files = unpacker.files
        
        classifiers_id, timeline_id = TableReader(table.Data)
        
        classifiers = tuple(file for file in files if file.ID in classifiers_id)
        timeline = next(file for file in files if file.ID == timeline_id)
        
        serializer = BinarySerializer()
        Timeline = serializer.Deserialize(timeline.Data)
        
        Timeline.write(path.join(output, f"{Timeline.general.Song}.tml"))
        os.makedirs(path.join(output, "classifiers"), exist_ok=True)
        
        for move in Timeline.databank.MoveBank:
            classifier = classifiers[move.CreationId]
            with open(path.join(output, "classifiers", f"{move.name}_{Timeline.general.Song}.{classifier.Type}".lower()), "wb") as f:
                f.write(classifier.Data)
        
        # Missing convert to BlueStar

        