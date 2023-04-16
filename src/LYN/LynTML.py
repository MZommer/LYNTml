from .BinaryReader import BinaryReader
import shutil
from io import BytesIO
import xml.etree.ElementTree as ET


class LynTML():
    def __init__(self):
        self.IsSpinOff = False
        self.HasXML = False
        self.layers = [
            [],  # Pictos
            [],  # Classifiers
            [],  # Events
            [],  # IDK?
            []  # Gestures
        ]
        self.CodeName = ""
        self.codename = ""
        self.markers = []
        self.names = []
        self.Classifiers = []
        self.beats = []
        self.Moves = [[], [], [], []]
        self.KinectMoves = [[], [], [], []]
        self.Pictos = []
        self.Lyrics = []
        self.Karaoke = []
        self.AmbientSounds = []
        self.GoldEffects = []
        self.Events = []
        self.Autodance = []
        self.HideUserInterface = []
        self.MSendBeat = 0
        self.previewStartTime, self.previewEndTime = 0, 0

    def makeJDNJSON(self):
        if self.beats[0] != 0:
            self.beats.insert(0, 0)
        if self.MSendBeat == 0:
            pass
        elif self.beats[-1] < self.MSendBeat:
            self.beats.append(self.MSendBeat)
        elif self.beats[-1] > self.MSendBeat:
            self.beats = self.beats[:self.beats.index(min(self.beats, key=lambda item: abs(item - self.MSendBeat)))]
            # For some reason the VirtualStart has more beats than the song lenght?
        main = {
            "MapName": self.CodeName,
            "Artist": self.CodeName,
            "Title": self.CodeName,
            "NumCoach": 1,
            "goldEffects": self.GoldEffects,
            "beats": self.beats,
            "lyrics": self.Karaoke if self.Karaoke != [] else self.Lyrics,
            "pictos": self.Pictos
        }
        if self.previewEndTime != 0:
            main["AudioPreview"] = {
                "entry": self.previewStartTime,
                "loopStart": 0,
                "loopEnd": self.previewEndTime,
                "offset": 0
            }
        if self.AmbientSounds:
            main["AmbientSounds"] = self.AmbientSounds
        if self.Autodance:
            main["autodances"] = self.Autodance
        if self.HideUserInterface:
            main["HideUserInterface"] = self.HideUserInterface
        return main

    def saveClassifiers(self, path):
        for index, classifier in enumerate(self.Classifiers):
            if classifier.startswith(b'GestureDetectorFile'):
                with open(f"{path}/{self.codename}_{self.layers[4][index].lower()}.gesture", "wb") as gesture:
                    gesture.write(b'GestureDetectorX360')
                    gesture.write(classifier[19:])
            else:
                # Live Move Classifier
                with open(f"{path}/{self.codename}_{self.layers[1][index].lower()}.lmc", "wb") as lmc:
                    lmc.write(classifier)

    def generatePlaceHolderPictos(self, path):
        for name in self.layers[0]:
            shutil.copy("./assets/Pictogram_1.png", f"{path}/{name.lower()}.png")

    def generatePlaceHolderClassifiers(self, path):
        for name in self.layers[1]:
            shutil.copy("./assets/Generic_generic.msm", f"{path}/{self.codename}_{name.lower()}.msm")

    ### Reader Functions ###
    def keyResolver(self, key):
        if key.startswith("Moves") or key.lower().startswith("kinectmoves"):
            return self.__parseMoves
        if key.lower().startswith("events"):
            return self.__parseEvents
        if key.lower().startswith("pictos"):
            return self.__parsePictos
        if key.lower().startswith("lyrics"):
            return self.__parseLyrics

        return {
            "BPM": self.__parseBPM,
            "Pictos": self.__parsePictos,
            "Lyrics": self.__parseLyrics,
            "Karaoke": self.__parseLyrics,
            "Preview": self.__parsePreview
        }[key]
        # TODO: refactor so it uses .get

    def Deserialize(self, path, parse=False):
        """A lot of unused values are just seeked since every read takes a lot"""
        self.binaryReader = BinaryReader("LITTLE", open(path, "rb"))
        self.binaryReader.fileStream.seek(4)
        offset = self.binaryReader.uint32()
        if offset > 0xFFFF:
            offset = self.binaryReader.uint32() + 8
            self.IsSpinOff = True
        self.binaryReader.fileStream.seek(offset + 0x22)
        classifierCount = self.binaryReader.uint32()
        firstClassifier_StringID = self.binaryReader.fileStream.read(4)
        bytearr = self.binaryReader.fileStream.read()
        # Bad aproach TODO: fix? probably a better approach would be just saving all files in the tml
        if b"\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x31\x2E\x30\x22\x20\x3F\x3E\x0A\x3C\x41\x6E\x6E\x6F\x74\x61\x74\x69\x6F\x6E\x46\x69\x6C\x65\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x32\x2E\x30\x22\x3E" in bytearr:
            self.HasXML = True
        self.binaryReader.fileStream.close()
        self.binaryReader.fileStream = BytesIO(bytearr[bytearr.index(firstClassifier_StringID):])
        """bad way to parse this but its the best way i found"""
        for _ in range(classifierCount):
            self.binaryReader.fileStream.seek(12 if self.IsSpinOff else 8, 1)  # StringID, IDK 2 sizeofs?
            self.Classifiers.append(self.binaryReader.fileStream.read(self.binaryReader.uint32()))
        self.binaryReader.fileStream.seek(12, 1)  # StringID, IDK 2 sizeofs?
        pos = self.binaryReader.fileStream.tell()
        Info_sizeOf = self.binaryReader.uint32()
        self.binaryReader.uint32()
        self.CodeName = self.binaryReader.string()
        self.codename = self.CodeName.lower()
        if parse: return self
        self.binaryReader.fileStream.seek(Info_sizeOf - (self.binaryReader.fileStream.tell() - pos), 1)
        self.__parseVirtualStart()
        self.__parseNames()
        self.__parseTimeLines()
        if self.HasXML:
            self.__parseKaraokeXML()

        self.__fixKaraoke()

        self.binaryReader.fileStream.close()

    def __fixKaraoke(self):
        """
         For some reason,
         the karaoke doesn't have an end line
         indicator so we gotta generate it
        """

        if not self.Karaoke:
            return
        # Probably a better approach is using the Lyrics
        # for making this but the lines are not the same on both
        lyricsIter = iter(self.Lyrics)
        actualClip = next(lyricsIter)
        buffer = ""
        karaokeLen = len(self.Karaoke) - 1
        for index, clip in enumerate(self.Karaoke):
            buffer += clip["text"]
            if actualClip["text"] == buffer or index == karaokeLen:
                clip["isLineEnding"] = 1
                buffer = ""
                try:
                    actualClip = next(lyricsIter)
                except StopIteration:
                    pass
            if actualClip["time"] + actualClip["duration"] <= clip["time"] + clip["duration"]:
                self.Karaoke[index - 1]["isLineEnding"] = 1
                buffer = ""
                try:
                    actualClip = next(lyricsIter)
                except StopIteration:
                    pass

    def __parseVirtualStart(self):
        sizeOf = self.binaryReader.uint32()
        self.binaryReader.uint32()  # idk?
        beatCount = self.binaryReader.uint32()
        self.binaryReader.uint32()  # idk?
        self.binaryReader.uint32()  # idk?
        self.binaryReader.string()  # VirtualStart
        for _ in range(beatCount - 1):
            startTime = self.binaryReader.float()
            endTime = self.binaryReader.float()
            name = self.binaryReader.string()
            self.beats.append(round(endTime * 1000))
            self.markers.append(round((endTime * 1000) * 48))

    def __parseNames(self):
        ENUMS_sizeOf = self.binaryReader.uint32()
        for _ in range(self.binaryReader.uint32()):
            pos = self.binaryReader.fileStream.tell()
            sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32()
            name = self.binaryReader.string()
            self.names.append(name)
            self.layers[layerID - 1].append(name)
            if not self.binaryReader.fileStream.tell() >= pos + sizeOf:
                self.binaryReader.fileStream.seek(sizeOf - (self.binaryReader.fileStream.tell() - pos), 1)

    def __parseTimeLines(self):
        sizeOf = self.binaryReader.uint32()
        for _ in range(self.binaryReader.uint32()):
            pos = self.binaryReader.fileStream.tell()
            _sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32() - 1
            itemCount = self.binaryReader.uint32()
            key = self.binaryReader.string()
            try:
                self.keyResolver(key)(key, _sizeOf, layerID, itemCount)
            except KeyError:
                print(f"NOT DESERIALIZING {key} ADD CLASS")
            self.binaryReader.fileStream.seek(_sizeOf - (
                    self.binaryReader.fileStream.tell() - pos), 1)  # Making sure its in place for the next class

    def __parseBPM(self, key, sizeOf, layerID, itemCount):
        q_ = self.binaryReader.float()
        a_ = self.binaryReader.uint32()
        c_ = self.binaryReader.uint32()
        v_ = self.binaryReader.uint32()
        endBeat = self.binaryReader.float() * 1000
        self.MSendBeat = round(endBeat)
        marker = round(endBeat * 48)
        if self.markers[-1] < marker:
            self.markers.append(marker)
        elif self.markers[-1] > self.MSendBeat:
            self.markers = self.markers[:self.markers.index(min(self.markers, key=lambda item: abs(item - marker)))]
        e_ = self.binaryReader.uint32()
        _ = self.binaryReader.uint32()
        self.BPM = self.binaryReader.float()

    def __parsePreview(self, key, sizeOf, layerID, itemCount):
        times = []
        for _ in range(itemCount):
            pos = self.binaryReader.fileStream.tell()
            sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32() - 1
            startTime = self.binaryReader.float()
            nameID = self.binaryReader.uint32()
            duration = self.binaryReader.float()
            times.append(startTime)
            self.binaryReader.fileStream.seek(sizeOf - (self.binaryReader.fileStream.tell() - pos), 1)
        self.previewStartTime, self.previewEndTime = times

    def __parseMoves(self, key, sizeOf, layerID, itemCount):
        arr = self.Moves[0] if not key[-1].isdigit() else self.Moves[
            int(key[-1]) - 1] if key.lower().startswith("moves") else self.KinectMoves[int(key[-1]) - 1]
        for _ in range(itemCount):
            pos = self.binaryReader.fileStream.tell()
            sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32() - 1
            startTime = self.binaryReader.float()
            nameID = self.binaryReader.uint32()
            duration = self.binaryReader.float()
            goldMove = self.binaryReader.uint32()
            arr.append({
                "name": f"{self.codename}_{self.names[nameID].lower()}",
                "time": round(startTime * 1000),
                "duration": round(duration * 1000),
                "goldMove": goldMove
            })
            while self.binaryReader.uint32() != 24:
                pass
            self.binaryReader.fileStream.seek(-4, 1)  # Making sure its in place for the next class

    def __parsePictos(self, key, sizeOf, layerID, itemCount):
        def existTime(time):
            for picto in self.Pictos:
                if picto["time"] == time:
                    return True
            return False

        try:
            delay = round(60000 / self.BPM)
        except:
            delay = 500
        for _ in range(itemCount):
            pos = self.binaryReader.fileStream.tell()
            sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32() - 1
            time = round(self.binaryReader.float() * 1000)
            nameID = self.binaryReader.uint32()
            self.binaryReader.fileStream.seek(sizeOf - (self.binaryReader.fileStream.tell() - pos), 1)

            if key == "Pictos":
                self.Pictos.append({
                    "name": self.names[nameID].lower(),
                    "time": time,
                    "duration": delay
                })
            else:
                name = self.names[nameID].lower().lstrip(f"{key[-1]}_")
                clip = {
                    "name": name,
                    "time": time,
                    "duration": delay
                }
                if not existTime(time):
                    self.Pictos.append(clip)
                    if name not in self.layers[0]:
                        self.layers[0].append(name)

    def __parseLyrics(self, key, sizeOf, layerID, itemCount):
        arr = self.Lyrics if key == "Lyrics" else self.Karaoke
        for _ in range(itemCount):
            pos = self.binaryReader.fileStream.tell()
            sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32() - 1
            startTime = self.binaryReader.float()
            duration = self.binaryReader.float()
            text = self.binaryReader.string(isLYN=True).encode("utf-8").decode("utf-8")
            arr.append({
                "time": round(startTime * 1000),
                "duration": round(duration * 1000),
                "text": text.replace("_", " "),
                "isLineEnding": 1 if key == "Lyrics" else 0
            })
            if not self.binaryReader.fileStream.tell() >= pos + sizeOf:
                self.binaryReader.fileStream.seek(sizeOf - (self.binaryReader.fileStream.tell() - pos), 1)

    def __parseKaraokeXML(self):
        self.binaryReader.fileStream.seek(12, 1)
        xmlString = self.binaryReader.string()
        tree = ET.fromstring(xmlString)
        for layer in tree:
            if layer.attrib["name"] == "lyrics":
                for interval in layer:
                    startTime = float(interval.attrib["t1"])
                    endTime = float(interval.attrib["t2"])
                    self.Karaoke.append({
                        "time": round(startTime * 1000),
                        "duration": round((endTime - startTime) * 1000),
                        "text": interval.attrib["value"].replace("$", ""),
                        "isLineEnding": 0
                    })

    def __parseEvents(self, key, sizeOf, layerID, itemCount):
        for _ in range(itemCount):
            pos = self.binaryReader.fileStream.tell()
            _sizeOf = self.binaryReader.uint32()
            layerID = self.binaryReader.uint32() - 1
            startTime = self.binaryReader.float()
            nameID = self.binaryReader.uint32()
            duration = self.binaryReader.float()
            eventType = self.binaryReader.uint32()
            _ = self.binaryReader.uint32()  # idk?
            __class = self.binaryReader.string()
            if __class == "PlaySnd":
                StopsOnEnd = self.binaryReader.uint32()
                id = self.binaryReader.uint32()
                self.AmbientSounds.append({
                    "name": self.names[nameID],
                    "time": round(startTime * 1000),
                    "duration": round(duration * 1000),
                    "StopsOnEnd": StopsOnEnd
                })
            elif __class == "GoldMove":
                self.GoldEffects.append({
                    "time": round(startTime * 1000),
                    "duration": round(duration * 1000)
                })
            elif __class == "RecordAutodance":
                self.Autodance.append({
                    "time": round(startTime * 1000),
                    "duration": round(duration * 1000)
                })
            else:
                print(f"NOT DESERIALIZING {__class} ADD CLASS")
            self.binaryReader.fileStream.seek(_sizeOf - (self.binaryReader.fileStream.tell() - pos), 1)
    ### End of Reader Functions ###
