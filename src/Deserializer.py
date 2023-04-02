from LYN.LynTML import LynTML
try:
    import BlueStar
    BLUESTAR_AVAILABLE = True
except ImportError:
    BLUESTAR_AVAILABLE = False
    print("BlueStar module is not available, please install or add to the folder.")
import os
import json

os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

for file in os.listdir("./input"):
    if os.path.isfile("./input/" + file):
        print(file)
        tml = LynTML()
        tml.Deserialize("./input/" + file)
        os.makedirs(f"./output/{tml.CodeName}", exist_ok=True)
        MainJson = tml.makeJDNJSON()
        json.dump(MainJson,
                  open(f"./output/{tml.CodeName}/{tml.CodeName}.json", "w", encoding="utf-8"),
                  ensure_ascii=False)
        for index, move in enumerate(tml.Moves):
            if move:
                json.dump(move, open(f"./output/{tml.CodeName}/{tml.CodeName}_Moves{index}.json", "w"))
        for index, move in enumerate(tml.KinectMoves):
            if move:
                json.dump(move, open(f"./output/{tml.CodeName}/{tml.CodeName}_KinectMoves{index}.json", "w"))
        os.makedirs(f"output/{tml.CodeName}/pictos", exist_ok=True)
        os.makedirs(f"output/{tml.CodeName}/classifiers", exist_ok=True)
        os.makedirs(f"output/{tml.CodeName}/classifiers/wiiu", exist_ok=True)
        tml.generatePlaceHolderPictos(f"output/{tml.CodeName}/pictos")
        tml.generatePlaceHolderClassifiers(f"output/{tml.CodeName}/classifiers/wiiu")
        tml.saveClassifiers(f"output/{tml.CodeName}/classifiers")
        if BLUESTAR_AVAILABLE:
            os.makedirs(f"output/{tml.CodeName}/UAF", exist_ok=True)
            song = BlueStar.Song(**MainJson, moves=tml.Moves, kinectMoves=tml.KinectMoves)
            song.makeUAF()
            UAF_PATH = f"output/{tml.CodeName}/UAF/{MainJson['MapName']}"
            os.makedirs(f"{UAF_PATH}/timeline", exist_ok=True)
            os.makedirs(f"{UAF_PATH}/audio", exist_ok=True)
            os.makedirs(f"{UAF_PATH}/cinematics", exist_ok=True)
            mapname = MainJson['MapName'].lower()
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