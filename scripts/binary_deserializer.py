import warnings
from collections.abc import Sequence
from pathlib import Path

from core.logger import logger
from core.serializers.xml import XMLSerializer
from lyn.binary_unpacker import File, Unpacker, save_file
from lyn.bluestar_converter import BlueStarConverter
from lyn.serializers.binary.timeline_serializer import TimelineSerializer
from lyn.table_reader import table_reader
from lyn.timeline.timeline import JustDanceToolLD

try:
    import BlueStar
except ImportError:
    BlueStar = None
    warnings.warn("BlueStar module missing! will not cook files for UAF.", stacklevel=2)
import json
import os
import shutil


def _unpack(table_file: os.PathLike, output: Path) -> tuple[File, tuple[File, ...]]:
    """Parameters
    ----------
    table_file : table to read files from.
    output : directory to write the files.

    Returns
    -------
    Timeline and Classifiers file objects.

    """
    unpacker = Unpacker.from_path(table_file)
    _header, table, *files = unpacker.files

    (output / "bin").mkdir(parents=True, exist_ok=True)
    for idx, file in enumerate(unpacker.files):
        save_file(file, output / "bin" / f"{idx}_{file.id}.{file.type}")

    classifiers_ids, timeline_id = table_reader(table.data)

    classifiers = tuple(file for file in files if file.id in classifiers_ids)
    timeline_file = next((file for file in files if file.id == timeline_id), None)
    assert timeline_file, "Timeline FileID not found in the files."
    return timeline_file, classifiers


def _save_lyn_classifiers(
    output: Path, timeline: JustDanceToolLD, classifiers: Sequence[File]
) -> None:
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


def _deserialize(file: os.PathLike, output: os.PathLike) -> JustDanceToolLD:
    output = Path(output)
    timeline_file, classifiers = _unpack(file, output)
    serializer = TimelineSerializer()
    timeline = serializer.deserialize(timeline_file.data)
    xml_serializer = XMLSerializer()
    xml_serializer.to_file(timeline, output / f"{timeline.partition.general.Song}.tml")
    _save_lyn_classifiers(output, timeline, classifiers)
    return timeline


def _generate_generic_classifiers(song_dir: Path, timeline: JustDanceToolLD) -> None:
    (song_dir / "classifiers" / "wiiu").mkdir(parents=True, exist_ok=True)
    if len(timeline.partition.databank.KinectMoveBank):
        (song_dir / "classifiers" / "x360").mkdir(exist_ok=True)
        (song_dir / "classifiers" / "orbis").mkdir(exist_ok=True)
        (song_dir / "classifiers" / "durango").mkdir(exist_ok=True)
        (song_dir / "classifiers" / "posenet").mkdir(exist_ok=True)

    for move in timeline.partition.databank.MoveBank:
        shutil.copy(
            "./assets/Generic_generic.msm",  # TODO: Take path from module.
            song_dir
            / "classifiers"
            / "wiiu"
            / f"{timeline.partition.general.Song.lower()}_{move.name}.msm",
        )

    for _gesture in timeline.partition.databank.KinectMoveBank:
        pass  # TODO: add generic gesture


def _generate_dummy_pictos(
    song_dir: Path, timeline: JustDanceToolLD, bluestar: BlueStarConverter
) -> None:
    (song_dir / "pictos").mkdir(exist_ok=True)

    for picto in timeline.partition.databank.PictoBank:
        shutil.copy(
            f"./assets/Pictogram_{bluestar.main['NumCoach'] + 1}.png",
            song_dir / "pictos" / f"{picto.name}.png",
        )


def _convert_to_bluestar(
    song_dir: Path, timeline: JustDanceToolLD
) -> BlueStarConverter:
    bluestar = BlueStarConverter(timeline)

    with open(
        song_dir / f"{timeline.partition.general.Song}.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(bluestar.main, f, ensure_ascii=False)
    for index, move in enumerate(bluestar.moves):
        if move:
            with open(
                song_dir / f"{timeline.partition.general.Song}_Moves{index}.json",
                "w",
            ) as f:
                json.dump(move, f)
    for index, move in enumerate(bluestar.kinectmoves):
        if move:
            with open(
                song_dir / f"{timeline.partition.general.Song}_KinectMoves{index}.json",
                "w",
            ) as f:
                json.dump(move, f)

    _generate_generic_classifiers(song_dir, timeline)
    _generate_dummy_pictos(song_dir, timeline, bluestar)
    return bluestar


def _cook_uaf_files(song_dir: Path, bluestar: BlueStarConverter) -> None:
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

            timeline = _deserialize(input_dir / file, output_dir / name)
            song_dir = output_dir / timeline.partition.general.Song
            song_dir.mkdir(exist_ok=True)
            bluestar = _convert_to_bluestar(song_dir, timeline)
            if BlueStar:
                _cook_uaf_files(song_dir, bluestar)


if __name__ == "__main__":
    main()
