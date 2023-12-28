from ..BinaryReader import BinaryReader
from io import BytesIO
from .__types__ import (
    Banks, Move, Gesture, Event, 
    Timeline,
    PictoLayer, MoveLayer, LyricsLayer, EventLayer,
    Instance, MoveInstance, LyricsInstance, EventInstance
)
from ..Logger import logger

# Decorator
def struct(func):
    def wrapper(self, *args, **kwargs):
        info = self._reader.InitStruct()
        ret = None
        try:
            ret = func(self, *args, **kwargs)
        except Exception as e:
            # ADD ROLLBACK
            logger.error(f"Error while parsing struct {func.__name__} {e}")
        
        if not self._reader.tell() >= info.seed + info.sizeOf:
            logger.debug(f"INCOMPLETE STRUCT {self._reader.tell()=} {info.seed=} {info.sizeOf=}")
        
        # Ensure pointer is at the end of the struct at the end of the function
        self._reader.seek(info.sizeOf - (self._reader.tell() - info.seed), 1)
        return ret
    return wrapper

class BinarySerializer:
    _reader: BinaryReader
    
    Timeline: Timeline
    
    # local state #
    virtualstart: list[float]
    
    def __init__(self) -> None:
        self.Timeline = Timeline()
        
        self.names = []
        self.virtualstart = []
        
    def Deserialize(self, stream: BytesIO) -> Timeline:
        if isinstance(stream, bytes):
            stream = BytesIO(stream)
        self._reader = BinaryReader("LITTLE", stream)
        self.__parseTimeline()
        return self.Timeline
    
    # Helper functions #    
    def getVirtualPosition(self, time):
        position = self.virtualstart.index(min(self.virtualstart, key=lambda item: abs(item - time)))
        offset = time - self.virtualstart[position]
        return position, offset
    
    # Reader functions #
    @struct
    def __parseTimeline(self):
        self.__parseGeneral()
        self.__parseVirtualStart()
        self.__parseDataBank()
        self.__parseLayers()
    
    @struct
    def __parseGeneral(self) -> None:
        self._reader.float()  # ??
        Song = self._reader.string()
        BeatsPerMeasure = self._reader.uint32()
        FirstMeasureMarkerPos = self._reader.uint32()
        BeatsPerMinute = self._reader.uint32()
        SampleFrequency = self._reader.uint32()
        WaveNbSamples = self._reader.uint32()
        CustomScoreSteps = bool(self._reader.uint32())
        
        for _ in range(self._reader.uint32()):
            Name = self._reader.string()
            Value = self._reader.uint32()
            self.Timeline.general.ScoreSteps.AddScoreStep(Name, Value)
        
        self.Timeline.general.Song = Song
        self.Timeline.general.BeatsPerMinute = BeatsPerMinute
        self.Timeline.general.SampleFrequency = SampleFrequency
        self.Timeline.general.BeatsPerMeasure = BeatsPerMeasure
        self.Timeline.general.FirstMeasureMarkerPos = FirstMeasureMarkerPos
        self.Timeline.general.WaveNbSamples = WaveNbSamples
        self.Timeline.general.CustomScoreSteps = CustomScoreSteps
        
        # Not serialized values #
        self.Timeline.general.WavePath = f".\Sounds\{Song}.wav"
        self.Timeline.general.VideoPath = f".\{Song}\Videos\{Song}.bik"
        self.Timeline.general.PictoFolder = ".\Pictos"
    
    @struct
    def __parseVirtualStart(self) -> None:
        self._reader.uint32()  # 0x00
        
        for position in range(self._reader.uint32()):
            sampleposition = self._reader.float()
            date = self._reader.float()
            name = self._reader.string()
            
            marker = self.Timeline.markerlist.AddMarker(position, name, sampleposition, date)
            
            self.virtualstart.append(date)

    @struct
    def __parseDataBank(self) -> None:
        for _ in range(self._reader.uint32()):
            self.__parseBank()

    @struct
    def __parseBank(self) -> None:
        bank = self._reader.uint32()
        name = self._reader.string()
        
        if bank == Banks.LYRICS:
            logger.debug("LYRICS BANK?")
        
        elif bank == Banks.PICTO:
            picto = self.Timeline.databank.AddPicto(name, len(self.Timeline.databank.PictoBank))
        
        elif bank == Banks.MOVE:
            move = self.__parseMove(name)
            
        elif bank == Banks.EVENTS:
            event = self.__parseEvent(name)
        
        elif bank == Banks.GESTURES:
            gesture = self.__parseGesture(name)
        
        else:
            logger.warning(f"UNKNOWN DATABANK {bank=}")
        
    
    def __parseMove(self, name: str) -> Move:
        CreationId = len(self.Timeline.databank.MoveBank)
        duration = 2
        SubdivisionsInBeat = 2
        color = "0x00000000" # Not serialized data?
        livemovemul = self._reader.float()
        livemoveplus = self._reader.float()
        Slack = self._reader.float()
        Capacity = self._reader.float()
        Stability = self._reader.float()
        GoldenMove = bool(self._reader.uint32())
        EnergyEvaluation = bool(self._reader.uint32())
        TimingEvaluation = bool(self._reader.uint32())
        CustomFloats = self._reader.vector()
        self._reader.uint32() # terminator?
        
        move = self.Timeline.databank.AddMove(name, CreationId, duration, SubdivisionsInBeat, color, livemovemul, livemoveplus, Slack, Capacity, Stability, GoldenMove, EnergyEvaluation, TimingEvaluation, CustomFloats)
        return move
    
    def __parseGesture(self, name: str) -> Gesture:
        CreationId = len(self.Timeline.databank.GesturesBank)
        duration = 2
        SubdivisionsInBeat = 2
        color = "0x00000000"
        gesturemul = self._reader.float()
        gestureplus = self._reader.float()
        Slack = self._reader.float()
        Capacity = self._reader.float()
        Stability = self._reader.float()
        GoldenMove = bool(self._reader.uint32())
        EnergyEvaluation = bool(self._reader.uint32())
        TimingEvaluation = bool(self._reader.uint32())
        CustomFloats = self._reader.vector()
        self._reader.uint32() # terminator?
        gesture = self.Timeline.databank.AddGesture(name, CreationId, duration, SubdivisionsInBeat, color, gesturemul, gestureplus, Slack, Capacity, Stability, GoldenMove, EnergyEvaluation, TimingEvaluation, CustomFloats)
        # TODO: add gesture struct
        return gesture
    
    def __parseEvent(self, name: str) -> Event:
        info = self._reader.GetStruct()
        struct_end = info.seed + info.sizeOf
        
        CreationId = len(self.Timeline.databank.EventsBank)
        DefaultDuration = self._reader.uint32()
        SubdivisionsInBeat = self._reader.uint32()
        event = self.Timeline.databank.AddEvent(name, CreationId, SubdivisionsInBeat, DefaultDuration)
        while not self._reader.tell() >= struct_end:
            paramName = self._reader.string()
            paramType = "Int" # TODO: add handler with known param names
            DisplayInTimeline = 1
            DefaultValue = ""
            event.AddParam(paramName, paramType, DisplayInTimeline, DefaultValue)
            # Not serialized values
        return event
    
    @struct
    def __parseLayers(self) -> None:
        for position in range(self._reader.uint32()):
            self.__parseLayer(position)
    @struct
    def __parseLayer(self, position: int) -> None:
        bank = self._reader.uint32()
        
        if bank == Banks.PICTO:
            layer = self.__parsePictoLayer(position)
        elif bank == Banks.MOVE or bank == Banks.GESTURES:
            layer = self.__parseMoveLayer(position)
        elif bank == Banks.EVENTS:
            layer = self.__parseEventLayer(position)
        elif bank == Banks.LYRICS:
            layer = self.__parseLyricsLayer(position)
        
        self.Timeline.append(layer)
        
    def __parsePictoLayer(self, position: int) -> PictoLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = PictoLayer(name, Banks.Id2Name(Banks.PICTO), position)
        for _ in range(entries):
            instance = self.__parsePictoInstance()
            layer.append(instance)
        return layer
    @struct
    def __parsePictoInstance(self) -> Instance:
        bank = self._reader.uint32()
        # TODO: add bank checker?
        date = self._reader.float()
        nameID = self._reader.uint32()
        position, offset = self.getVirtualPosition(date)
        return Instance(position, self.Timeline.databank.get(nameID), date)

    def __parseMoveLayer(self, position: int) -> MoveLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = MoveLayer(name, Banks.Id2Name(Banks.MOVE), position)
        for _ in range(entries):
            instance = self.__parseMoveInstance()
            layer.append(instance)
            self._reader.uint32()
            self._reader.uint32() 
            # out of the sizeof struct but the next struct is shifted?            
        return layer
    @struct
    def __parseMoveInstance(self) -> MoveInstance:
        bank = self._reader.uint32()
        date = self._reader.float()
        nameID = self._reader.uint32()
        duration = self._reader.float()
        GoldMove = bool(self._reader.uint32())
        
        position, offset = self.getVirtualPosition(date)
        OffsetInSubdivisions = self.getVirtualPosition(date + duration)[0] - position
        return MoveInstance(position, self.Timeline.databank.get(nameID), date, duration, GoldMove, OffsetInSubdivisions)
    
    def __parseEventLayer(self, position: int) -> EventLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = EventLayer(name, Banks.Id2Name(Banks.EVENTS), position)
        for _ in range(entries):
            instance = self.__parseEventInstance()
            layer.append(instance)
        return layer
    
    @struct
    def __parseEventInstance(self) -> EventInstance:
        bank = self._reader.uint32()
        date = self._reader.float()
        nameID = self._reader.uint32()
        name = self.Timeline.databank.get(nameID)
        length = self._reader.float()
        color = "0x00000000"
        DefaultDuration = self._reader.uint32()
        SubdivisionsInBeat = self._reader.uint32()
        position, offset = self.getVirtualPosition(date)
        event = EventInstance(position, name, offset, length, color)
        for param in self.Timeline.databank.find(name).Params:
            if param.type == "String":
                value = self._reader.string()
            elif param.type == "Float":
                value = self._reader.float()
            else:
                value = self._reader.uint32()
            event.AddParam(param.name, value)
        return event
      
    
    def __parseLyricsLayer(self, position: int) -> LyricsLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = LyricsLayer(name, Banks.Id2Name(Banks.LYRICS), position)
        for _ in range(entries):
            instance = self.__parseLyricsInstance()
            layer.append(instance)
        return layer
    @struct
    def __parseLyricsInstance(self) -> LyricsInstance:
        bank = self._reader.uint32()
        date = self._reader.float()
        length = self._reader.float()
        text = self._reader.string(True).encode("utf-8").decode("utf-8")
        
        position, offset = self.getVirtualPosition(date)
        return LyricsInstance(position, "Lyrics", date, length, text)

