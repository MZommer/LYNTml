from pathlib import Path

from core.logger import logger
from core.serializers.xml import XMLSerializer
from LyN.binary_unpacker import Unpacker, save_file
from LyN.bluestar_converter import BlueStarConverter
from LyN.serializers.binary.timeline_serializer import TimelineSerializer
from LyN.table_reader import table_reader
from LyN.timeline.timeline import JustDanceToolLD

try:
    import BlueStar
except ImportError:
    BlueStar = None
import json
import os
import shutil


def unpack_and_decode(file: os.PathLike, output: os.PathLike) -> JustDanceToolLD:
    output = Path(output)
    unpacker = Unpacker.from_path(file)
    _header, table, *files = unpacker.files

    (output / "bin").mkdir(parents=True, exist_ok=True)
    for idx, file in enumerate(unpacker.files):
        save_file(file, output / "bin" / f"{idx}_{file.id}.{file.type}")

    classifiers_ids, timeline_id = table_reader(table.data)

    classifiers = tuple(file for file in files if file.id in classifiers_ids)
    timeline_file = next(file for file in files if file.id == timeline_id)

    serializer = TimelineSerializer()
    timeline = serializer.deserialize(timeline_file.data)
    xml_serializer = XMLSerializer()
    xml_serializer.to_file(timeline, output / f"{timeline.partition.general.Song}.tml")
    classifiers_dir = output / "classifiers"
    classifiers_dir.mkdir(exist_ok=True)
    for idx, move in enumerate(timeline.partition.databank.MoveBank):
        try:
            classifier = classifiers[idx]
        except IndexError:
            logger.exception(f"Missing classifier {move.name}")
            continue
        classifier_path = (
            classifiers_dir
            / f"{move.name}_{timeline.partition.general.Song}.{classifier.type}".lower()
        )
        with open(classifier_path, "wb") as f:
            f.write(classifier.data)

    return timeline


def main() -> None:
    input_dir = Path("input")
    output_dir = Path("output")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    for file in os.listdir(input_dir):
        input_file = input_dir / file
        if input_file.is_file():
            name = input_file.stem
            (output_dir / name).mkdir(exist_ok=True)

            timeline = unpack_and_decode(input_dir / file, output_dir / name)
            bluestar = BlueStarConverter(timeline)

            song_dir = output_dir / timeline.partition.general.Song
            song_dir.mkdir(exist_ok=True)

            with open(
                song_dir / f"{timeline.partition.general.Song}.json",
                "w",
                encoding="utf-8",
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

            (song_dir / "pictos").mkdir(exist_ok=True)
            (song_dir / "classifiers" / "wiiu").mkdir(parents=True, exist_ok=True)
            if len(timeline.partition.databank.KinectMoveBank):
                (song_dir / "classifiers" / "x360").mkdir(exist_ok=True)
                (song_dir / "classifiers" / "orbis").mkdir(exist_ok=True)
                (song_dir / "classifiers" / "durango").mkdir(exist_ok=True)
                (song_dir / "classifiers" / "posenet").mkdir(exist_ok=True)

            for picto in timeline.partition.databank.PictoBank:
                shutil.copy(
                    f"./assets/Pictogram_{bluestar.main['NumCoach'] + 1}.png",
                    song_dir / "pictos" / f"{picto.name}.png",
                )

            for move in timeline.partition.databank.MoveBank:
                shutil.copy(
                    "./assets/Generic_generic.msm",
                    song_dir
                    / "classifiers"
                    / "wiiu"
                    / f"{timeline.partition.general.Song.lower()}_{move.name}.msm",
                )

            for _gesture in timeline.partition.databank.KinectMoveBank:
                pass  # TODO: add generic gesture

            if BlueStar:
                (song_dir / "UAF").mkdir(exist_ok=True)
                song = BlueStar.Song(
                    **bluestar.main,
                    moves=bluestar.moves,
                    kinectMoves=bluestar.kinectmoves,
                )
                song.makeUAF()
                uaf_path = song_dir / "UAF" / bluestar.main["MapName"]
                (uaf_path / "timeline").mkdir(exist_ok=True)
                (uaf_path / "audio").mkdir(exist_ok=True)
                (uaf_path / "cinematics").mkdir(exist_ok=True)
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
                    (uaf_path / "audio" / "amb").mkdir(exist_ok=True)
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
