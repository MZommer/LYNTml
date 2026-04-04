from pathlib import Path

from LyN.binary_unpacker import Unpacker
from LyN.bluestar_converter import BlueStarConverter
from LyN.logger import logger
from LyN.table_reader import table_reader
from LyN.Timeline.BinarySerializer import BinarySerializer
from LyN.Timeline.timeline import JustDanceToolLD

try:
    import BlueStar
except ImportError:
    BlueStar = None
import json
import os
import shutil


def unpack_and_decode(file: os.PathLike, output: os.PathLike) -> JustDanceToolLD:
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
            continue
        classifier_path = os.path.join(
            output,
            "classifiers",
            f"{move.name}_{timeline.general.Song}.{classifier.type}".lower(),
        )
        with open(classifier_path, "wb") as f:
            f.write(classifier.data)

    return timeline


def main() -> None:
    input_dir = Path("input")
    output_dir = Path("output")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        input_file = input_dir / file
        if input_file.is_file():
            name = input_file.stem
            os.makedirs(output_dir / name, exist_ok=True)

            timeline = unpack_and_decode(input_dir / file, output_dir / name)
            bluestar = BlueStarConverter(timeline)

            song_dir = output_dir / timeline.partition.general.Song
            os.makedirs(song_dir, exist_ok=True)

            with open(
                song_dir / f"{timeline.general.Song}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(bluestar.main, f, ensure_ascii=False)
            for index, move in enumerate(bluestar.moves):
                if move:
                    with open(
                        song_dir
                        / f"{timeline.partition.general.Song}_Moves{index}.json",
                        "w",
                    ) as f:
                        json.dump(move, f)
            for index, move in enumerate(bluestar.kinectmoves):
                if move:
                    with open(
                        song_dir
                        / f"{timeline.partition.general.Song}_KinectMoves{index}.json",
                        "w",
                    ) as f:
                        json.dump(move, f)

            os.makedirs(song_dir / "pictos", exist_ok=True)
            os.makedirs(song_dir / "classifiers" / "wiiu", exist_ok=True)
            if len(timeline.partition.databank.KinectMoveBank):
                os.makedirs(song_dir / "classifiers" / "x360", exist_ok=True)
                os.makedirs(song_dir / "classifiers" / "orbis", exist_ok=True)
                os.makedirs(song_dir / "classifiers" / "durango", exist_ok=True)
                os.makedirs(song_dir / "classifiers" / "posenet", exist_ok=True)

            for picto in timeline.partition.databank.PictoBank:
                shutil.copy(
                    f"./assets/Pictogram_{bluestar.main['NumCoach']}.png",
                    song_dir / "pictos" / f"{picto.name}.png",
                )

            for move in timeline.partition.databank.MoveBank:
                shutil.copy(
                    "./assets/Generic_generic.msm",
                    song_dir
                    / "classifiers"
                    / "wiiu"
                    / f"{timeline.general.Song.lower()}_{move.name}.msm",
                )

            for _gesture in timeline.partition.databank.KinectMoveBank:
                pass  # TODO: add generic gesture

            if BlueStar:
                os.makedirs(song_dir / "UAF", exist_ok=True)
                song = BlueStar.Song(
                    **bluestar.main,
                    moves=bluestar.moves,
                    kinectMoves=bluestar.kinectmoves,
                )
                song.makeUAF()
                uaf_path = song_dir / "UAF" / bluestar.main["MapName"]
                os.makedirs(uaf_path / "timeline", exist_ok=True)
                os.makedirs(uaf_path / "audio", exist_ok=True)
                os.makedirs(uaf_path / "cinematics", exist_ok=True)
                mapname = bluestar.main["MapName"].lower()
                with open(
                    uaf_path / "timeline" / f"{mapname}_tml_dance.dtape.ckd",
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(song.tml_dance, f, ensure_ascii=False)
                with open(
                    uaf_path / "timeline" / f"{mapname}_tml_karaoke.ktape.ckd",
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(song.tml_karaoke, f, ensure_ascii=False)
                with open(
                    uaf_path / "cinematics" / f"{mapname}_mainsequence.tape.ckd",
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(song.mainsequence, f, ensure_ascii=False)
                with open(
                    uaf_path / "audio" / f"{mapname}_musictrack.tpl.ckd",
                    "w",
                    encoding="utf-8",
                ) as f:
                    json.dump(song.musictrack, f, ensure_ascii=False)
                if song.ambtpls:
                    os.makedirs(uaf_path / "audio" / "amb", exist_ok=True)
                for index, amb in enumerate(song.ambtpls):
                    with open(
                        uaf_path / "audio" / "amb" / f"amb_{mapname}_{index}.tpl.ckd",
                        "w",
                        encoding="utf-8",
                    ) as f:
                        json.dump(amb, f, ensure_ascii=False)
                with open(uaf_path / "songdesc.tpl.ckd", "w", encoding="utf-8") as f:
                    json.dump(song.songdesc, f, ensure_ascii=False)


if __name__ == "__main__":
    main()
