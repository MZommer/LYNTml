from pathlib import Path

from LYN.BlueStarConverter import BlueStarConverter
from LYN.LyN import LyN

try:
    import BlueStar
except ImportError:
    BlueStar = None
    print("BlueStar module is not available, please install or add to the folder.")
import os
import json
import shutil

input_dir = Path("input")
output_dir = Path("output")
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(input_dir):
    input_file = input_dir / file
    if input_file.is_file():
        print(file)

        name = input_file.stem
        os.makedirs(output_dir / name, exist_ok=True)

        timeline = LyN.UnpackAndDecode(input_dir / file, output_dir / name)
        try:
            bluestar = BlueStarConverter(timeline)
        except Exception as e:
            print("An error occurred while converting song to BlueStar\n", e)
            continue

        song_dir = output_dir / timeline.general.Song
        os.makedirs(song_dir, exist_ok=True)

        with open(song_dir / f"{timeline.general.Song}.json", "w", encoding="utf-8") as f:
            json.dump(bluestar.main, f, ensure_ascii=False)
        for index, move in enumerate(bluestar.moves):
            if move:
                with open(song_dir / f"{timeline.general.Song}_Moves{index}.json", "w") as f:
                    json.dump(move, f)
        for index, move in enumerate(bluestar.kinectmoves):
            if move:
                with open(song_dir / f"{timeline.general.Song}_KinectMoves{index}.json", "w") as f:
                    json.dump(move, f)

        os.makedirs(song_dir / "pictos", exist_ok=True)
        os.makedirs(song_dir / "classifiers" / "wiiu", exist_ok=True)
        if len(timeline.databank.GestureBank):
            os.makedirs(song_dir / "classifiers" / "x360", exist_ok=True)
            os.makedirs(song_dir / "classifiers" / "orbis", exist_ok=True)
            os.makedirs(song_dir / "classifiers" / "durango", exist_ok=True)
            os.makedirs(song_dir / "classifiers" / "posenet", exist_ok=True)

        for picto in timeline.databank.PictoBank:
            shutil.copy(f"./assets/Pictogram_{bluestar.main['NumCoach']}.png",
                        song_dir / "pictos" / f"{picto.name}.png")

        for move in timeline.databank.MoveBank:
            shutil.copy("./assets/Generic_generic.msm",
                        song_dir / "classifiers" / "wiiu" / f"{timeline.general.Song.lower()}_{move.name}.msm")

        for gesture in timeline.databank.GestureBank:
            pass  # TODO: add generic gesture

        if BlueStar:
            os.makedirs(song_dir / "UAF", exist_ok=True)
            song = BlueStar.Song(**bluestar.main, moves=bluestar.moves, kinectMoves=bluestar.kinectmoves)
            song.makeUAF()
            uaf_path = song_dir / "UAF" / bluestar.main['MapName']
            os.makedirs(uaf_path / "timeline", exist_ok=True)
            os.makedirs(uaf_path / "audio", exist_ok=True)
            os.makedirs(uaf_path / "cinematics", exist_ok=True)
            mapname = bluestar.main['MapName'].lower()
            with open(uaf_path / "timeline" / f"{mapname}_tml_dance.dtape.ckd", "w", encoding="utf-8") as f:
                json.dump(song.tml_dance, f, ensure_ascii=False)
            with open(uaf_path / "timeline" / f"{mapname}_tml_karaoke.ktape.ckd", "w", encoding="utf-8") as f:
                json.dump(song.tml_karaoke, f, ensure_ascii=False)
            with open(uaf_path / "cinematics" / f"{mapname}_mainsequence.tape.ckd", "w", encoding="utf-8") as f:
                json.dump(song.mainsequence, f, ensure_ascii=False)
            with open(uaf_path / "audio" / f"{mapname}_musictrack.tpl.ckd", "w", encoding="utf-8") as f:
                json.dump(song.musictrack, f, ensure_ascii=False)
            if song.ambtpls:
                os.makedirs(uaf_path / "audio" / "amb", exist_ok=True)
            for index, amb in enumerate(song.ambtpls):
                with open(uaf_path / "audio" / "amb" / f"amb_{mapname}_{index}.tpl.ckd", "w", encoding="utf-8") as f:
                    json.dump(amb, f, ensure_ascii=False)
            with open(uaf_path / "songdesc.tpl.ckd", "w", encoding="utf-8") as f:
                json.dump(song.songdesc, f, ensure_ascii=False)
