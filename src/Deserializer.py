from LYN.LyN import LyN
from LYN.BlueStarConverter import BlueStarConverter
try:
    import BlueStar
    BLUESTAR_AVAILABLE = True
except ImportError:
    BLUESTAR_AVAILABLE = False
    print("BlueStar module is not available, please install or add to the folder.")
import os
import json
import shutil

os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

for file in os.listdir("./input"):
    if os.path.isfile("./input/" + file):
        name = file.split(".")[0]
        os.makedirs("output/" + name, exist_ok=True)
        
        print(file)
        
        timeline = LyN.UnpackAndDecode("./input/" + file, "output/"+name)
        
        bluestar = BlueStarConverter(timeline)
                
        os.makedirs(f"./output/{timeline.general.Song}", exist_ok=True)

        json.dump(bluestar.main,
                  open(f"./output/{timeline.general.Song}/{timeline.general.Song}.json", "w", encoding="utf-8"),
                  ensure_ascii=False)
        for index, move in enumerate(bluestar.moves):
            if move:
                json.dump(move, open(f"./output/{timeline.general.Song}/{timeline.general.Song}_Moves{index}.json", "w"))
        for index, move in enumerate(bluestar.kinectmoves):
            if move:
                json.dump(move, open(f"./output/{timeline.general.Song}/{timeline.general.Song}_KinectMoves{index}.json", "w"))
        
        os.makedirs(f"output/{timeline.general.Song}/pictos", exist_ok=True)
        os.makedirs(f"output/{timeline.general.Song}/classifiers/wiiu", exist_ok=True)
        if timeline.databank.GestureBank:
            os.makedirs(f"output/{timeline.general.Song}/classifiers/x360", exist_ok=True)
            os.makedirs(f"output/{timeline.general.Song}/classifiers/orbis", exist_ok=True)
            os.makedirs(f"output/{timeline.general.Song}/classifiers/durango", exist_ok=True)
            os.makedirs(f"output/{timeline.general.Song}/classifiers/posenet", exist_ok=True)
        
        for picto in timeline.databank.PictoBank:
            shutil.copy(f"assets/Pictogram_{bluestar.main.get('NumCoach', 1)}.png", f"output/{timeline.general.Song}/pictos/{picto.name}.png")
        
        for move in timeline.databank.MoveBank:
            shutil.copy("assets/Generic_generic.msm", f"output/{timeline.general.Song}/classifiers/wiiu/{timeline.general.Song.lower()}_{move.name}.msm")
        
        for gesture in timeline.databank.GestureBank:
            pass # TODO: add generic gesture
        
        if BLUESTAR_AVAILABLE:
            os.makedirs(f"output/{timeline.general.Song}/UAF", exist_ok=True)
            song = BlueStar.Song(**bluestar.main, moves=bluestar.Moves, kinectMoves=bluestar.KinectMoves)
            song.makeUAF()
            UAF_PATH = f"output/{timeline.general.Song}/UAF/{bluestar.main['MapName']}"
            os.makedirs(f"{UAF_PATH}/timeline", exist_ok=True)
            os.makedirs(f"{UAF_PATH}/audio", exist_ok=True)
            os.makedirs(f"{UAF_PATH}/cinematics", exist_ok=True)
            mapname = bluestar.main['MapName'].lower()
            json.dump(song.tml_dance,
                      open(f"{UAF_PATH}/timeline/{mapname}_tml_dance.dtape.ckd", "w", encoding="utf-8"),
                      ensure_ascii=False)
            json.dump(song.tml_karaoke,
                      open(f"{UAF_PATH}/timeline/{mapname}_tml_karaoke.ktape.ckd", "w", encoding="utf-8"),
                      ensure_ascii=False)
            json.dump(song.mainsequence,
                      open(f"{UAF_PATH}/cinematics/{mapname}_mainsequence.tape.ckd", "w", encoding="utf-8"),
                      ensure_ascii=False)
            json.dump(song.musictrack,
                      open(f"{UAF_PATH}/audio/{mapname}_musictrack.tpl.ckd", "w", encoding="utf-8"),
                      ensure_ascii=False)
            for index, amb in enumerate(song.ambtpls):
                os.makedirs(f"{UAF_PATH}/audio/amb", exist_ok=True)
                json.dump(amb,
                          open(f"{UAF_PATH}/audio/amb/amb_{mapname}_{index}.tpl.ckd", "w", encoding="utf-8"),
                          ensure_ascii=False)
            json.dump(song.songdesc,
                      open(f"{UAF_PATH}/songdesc.tpl.ckd", "w", encoding="utf-8"),
                      ensure_ascii=False)