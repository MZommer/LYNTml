import xml.etree.ElementTree as ET

class Banks:
    LYRICS = 0
    PICTO = 1
    MOVE = 2
    EVENTS = 3
    GESTURES = 5
    
    @staticmethod
    def Id2Name(id: int) -> str:
        return {
            0: "Lyrics",
            1: "Picto",
            2: "Move",
            3: "Events",
            5: "Gestures"
        }[id]


class Picto(ET.Element):
    name: str
    CreationId: int
    offset: float
    
    def __init__(self, name: str, CreationId: int, offset: float = None) -> None:
        super().__init__("Picto", attrib={
            "name": str(name),
            "CreationId": str(CreationId),
        })
        if offset:
            ET.SubElement(self, "offset").text = str(offset)
    
    @property
    def name(self) -> str:
        return self.attrib["name"]
    @name.setter
    def name(self, value: str) -> None:
        self.attrib["name"] = str(value)
        
    @property
    def CreationId(self) -> int:
        return int(self.attrib["CreationId"])
    @CreationId.setter
    def CreationId(self, value: int) -> None:
        self.attrib["CreationId"] = str(value)
    
    @property
    def offset(self) -> float:
        return float(self.find("offset").text)
    @offset.setter
    def offset(self, value: float) -> None:
        self.find("offset").text = str(value)
        
class PictoBank(ET.Element):
    def __init__(self) -> None:
        super().__init__("PictoBank")

    def AddPicto(self, name: str, CreationId: int, offset: float = None) -> Picto:
        picto = Picto(name, CreationId, offset)
        self.append(picto)
        return picto
    
class Move(ET.Element):
    name: str
    CreationId: int
    durationElement: ET.Element
    SubdivisionsInBeatElement: ET.Element
    colorElement: ET.Element
    livemovemulElement: ET.Element
    livemoveplusElement: ET.Element
    SlackElement: ET.Element
    CapacityElement: ET.Element
    StabilityElement: ET.Element
    GoldenMoveElement: ET.Element
    EnergyEvaluationElement: ET.Element
    TimingEvaluationElement: ET.Element
    CustomFloatsElement: ET.Element
    
    def __init__(self, name: str, CreationId: int, duration: int, SubdivisionsInBeat: int, color: str, livemovemul: float, livemoveplus: float, Slack: float, Capacity: float, Stability: float, GoldenMove: bool, EnergyEvaluation: bool, TimingEvaluation: bool, CustomFloats: tuple[float]) -> None:
        super().__init__("Move")
        self.name = name
        self.CreationId = CreationId
        
        self.durationElement = ET.SubElement(self, "duration")
        self.duration = duration
        self.SubdivisionsInBeatElement = ET.SubElement(self, "SubdivisionsInBeat")
        self.SubdivisionsInBeat = SubdivisionsInBeat
        self.colorElement = ET.SubElement(self, "color")
        self.color = color
        self.livemovemulElement = ET.SubElement(self, "livemovemul")
        self.livemovemul = livemovemul
        self.livemoveplusElement = ET.SubElement(self, "livemoveplus")
        self.livemoveplus = livemoveplus
        self.SlackElement = ET.SubElement(self, "Slack")
        self.Slack = Slack
        self.CapacityElement = ET.SubElement(self, "Capacity")
        self.Capacity = Capacity
        self.StabilityElement = ET.SubElement(self, "Stability")
        self.Stability = Stability
        self.GoldenMoveElement = ET.SubElement(self, "GoldenMove")
        self.GoldenMove = GoldenMove
        self.EnergyEvaluationElement = ET.SubElement(self, "EnergyEvaluation")
        self.EnergyEvaluation = EnergyEvaluation
        self.TimingEvaluationElement = ET.SubElement(self, "TimingEvaluation")
        self.TimingEvaluation = TimingEvaluation
        self.CustomFloatsElement = ET.SubElement(self, "CustomFloats")
        self.CustomFloats = CustomFloats

    @property
    def name(self) -> str:
        return self.attrib["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.attrib["name"] = str(value)

    @property
    def CreationId(self) -> int:
        return int(self.attrib["CreationId"])

    @CreationId.setter
    def CreationId(self, value: int) -> None:
        self.attrib["CreationId"] = str(value)

    @property
    def duration(self) -> int:
        return int(self.durationElement.text)

    @duration.setter
    def duration(self, value: int) -> None:
        self.durationElement.text = str(value)

    @property
    def SubdivisionsInBeat(self) -> int:
        return int(self.SubdivisionsInBeatElement.text)

    @SubdivisionsInBeat.setter
    def SubdivisionsInBeat(self, value: int) -> None:
        self.SubdivisionsInBeatElement.text = str(value)
    
    @property
    def color(self) -> str:
        return self.colorElement.text

    @color.setter
    def color(self, value: str) -> None:
        self.colorElement.text = str(value)

    @property
    def livemovemul(self) -> float:
        return float(self.livemovemulElement.text)

    @livemovemul.setter
    def livemovemul(self, value: float) -> None:
        self.livemovemulElement.text = str(value)

    @property
    def livemoveplus(self) -> float:
        return float(self.livemoveplusElement.text)

    @livemoveplus.setter
    def livemoveplus(self, value: float) -> None:
        self.livemoveplusElement.text = str(value)

    @property
    def Slack(self) -> float:
        return float(self.SlackElement.text)

    @Slack.setter
    def Slack(self, value: float) -> None:
        self.SlackElement.text = str(value)

    @property
    def Capacity(self) -> float:
        return float(self.CapacityElement.text)

    @Capacity.setter
    def Capacity(self, value: float) -> None:
        self.CapacityElement.text = str(value)

    @property
    def Stability(self) -> float:
        return float(self.StabilityElement.text)

    @Stability.setter
    def Stability(self, value: float) -> None:
        self.StabilityElement.text = str(value)

    @property
    def GoldenMove(self) -> bool:
        return self.GoldenMoveElement.text == "True"

    @GoldenMove.setter
    def GoldenMove(self, value: bool) -> None:
        if isinstance(value, str):
            value = value == "True"
        self.GoldenMoveElement.text = str(bool(value))

    @property
    def EnergyEvaluation(self) -> bool:
        return self.EnergyEvaluationElement.text == "True"

    @EnergyEvaluation.setter
    def EnergyEvaluation(self, value: bool) -> None:
        if isinstance(value, str):
            value = value == "True"
        self.EnergyEvaluationElement.text = str(bool(value))

    @property
    def TimingEvaluation(self) -> bool:
        return self.TimingEvaluationElement.text == "True"

    @TimingEvaluation.setter
    def TimingEvaluation(self, value: float) -> None:
        if isinstance(value, str):
            value = value == "True"
        self.TimingEvaluationElement.text = str(bool(value))

    @property
    def CustomFloats(self) -> str:
        return [float(i) for i in self.CustomFloatsElement.text.split(';')]

    @CustomFloats.setter
    def CustomFloats(self, value: list[float]) -> None:
        if isinstance(value, str):
            self.CustomFloatsElement.text = value
        else:
            self.CustomFloatsElement.text = ';'.join(tuple(str(i) for i in value))

class MoveBank(ET.Element):
    def __init__(self) -> None:
        super().__init__("MoveBank")
    
    def AddMove(self, name: str, CreationId: int, duration: int, SubdivisionsInBeat: int, color: str, livemovemul: float, livemoveplus: float, Slack: float, Capacity: float, Stability: float, GoldenMove: bool, EnergyEvaluation: bool, TimingEvaluation: bool, CustomFloats: tuple[float]) -> Move:
        move = Move(name, CreationId, duration, SubdivisionsInBeat, color, livemovemul, livemoveplus, Slack, Capacity, Stability, GoldenMove, EnergyEvaluation, TimingEvaluation, CustomFloats)
        self.append(move)
        return move

class Event(ET.Element):
    class Param(ET.Element):
        name: str
        type: str
        DisplayInTimeline: int
        DefaultValue: str
        
        @staticmethod
        def TypeResolver(name: str) -> str:
            return {
                "Class": "String",
                
                "Forward": "Float",
                "Backward": "Float",
                "Right": "Float",
                "Left": "Float",
                "Down": "Float",
                "StartOffset": "Float",
                "BPM": "Float",
                
                "Target": "Bool",
            }.get(name, "Int")
        
        def __init__(self, name: str, type: str = '', DisplayInTimeline: int = 1, DefaultValue: str = '') -> None:
            super().__init__("Param")
            self.name = name or " New Param"
            self.type = self.TypeResolver(name)
            self.DisplayInTimeline = DisplayInTimeline
            self.DefaultValue = DefaultValue
        
        def __repr__(self) -> str:
            return f"Param({self.name}, {self.type}, {self.DisplayInTimeline}, {self.DefaultValue})"
        
        @property
        def name(self) -> str:
            return self.attrib["name"]
        @name.setter
        def name(self, value: str) -> None:
            self.attrib["name"] = str(value)
        
        @property
        def type(self) -> str:
            return self.attrib["type"]
        @type.setter
        def type(self, value: str) -> None:
            self.attrib["type"] = str(value)
        
        @property
        def DisplayInTimeline(self) -> int:
            return int(self.attrib["DisplayInTimeline"])
        @DisplayInTimeline.setter
        def DisplayInTimeline(self, value: int) -> None:
            self.attrib["DisplayInTimeline"] = str(value)
        
        @property
        def DefaultValue(self) -> str:
            return self.attrib["DefaultValue"]
        @DefaultValue.setter
        def DefaultValue(self, value: str) -> None:
            self.attrib["DefaultValue"] = str(value)
        
    name: str
    CreationId: int
    SubdivisionsInBeat: ET.Element
    DefaultDuration: ET.Element
    Params: ET.Element
    
    def __init__(self, name: str, CreationId: int, SubDivisionsInBeat: int, DefaultDuration: int) -> None:
        super().__init__("Event")
        self.name = name
        self.CreationId = CreationId
        self.DefaultDuration = ET.SubElement(self, "DefaultDuration")
        self.DefaultDuration.text = str(DefaultDuration)
        self.SubdivisionsInBeat = ET.SubElement(self, "SubdivisionsInBeat")
        self.SubdivisionsInBeat.text = str(SubDivisionsInBeat)
        self.Params = ET.SubElement(self, "Params")
    
    def AddParam(self, name: str, type: str = '', DisplayInTimeline: int = 1, DefaultValue: str = '') -> None:
        param = Event.Param(name, type, DisplayInTimeline, DefaultValue)
        self.Params.append(param)
        return param
    
    @property
    def name(self) -> str:
        return self.attrib["name"]
    @name.setter
    def name(self, value: str) -> None:
        self.attrib["name"] = str(value)
    
    @property
    def CreationId(self) -> int:
        return int(self.attrib["CreationId"])
    @CreationId.setter
    def CreationId(self, value: int) -> None:
        self.attrib["CreationId"] = str(value)

class EventsBank(ET.Element):
    def __init__(self) -> None:
        super().__init__("EventsBank")
    
    def AddEvent(self, name: str, CreationId: int, SubDivisionsInBeat: int, DefaultDuration: int) -> Event:
        event = Event(name, CreationId, SubDivisionsInBeat, DefaultDuration)
        self.append(event)
        return event

class LyricsBank(ET.Element):
    def __init__(self, CreationId: int = 0) -> None:
        super().__init__("LyricsBank")
        ET.SubElement(self, "Lyrics", attrib={"name": "lyrics", "CreationId": str(CreationId)})

class Gesture(ET.Element):
    name: str
    CreationId: int
    durationElement: ET.Element
    SubdivisionsInBeatElement: ET.Element
    colorElement: ET.Element
    gesturemulElement: ET.Element
    gestureplusElement: ET.Element
    SlackElement: ET.Element
    CapacityElement: ET.Element
    StabilityElement: ET.Element
    GoldenMoveElement: ET.Element
    EnergyEvaluationElement: ET.Element
    TimingEvaluationElement: ET.Element
    CustomFloatsElement: ET.Element
    
    def __init__(self, name: str, CreationId: int, duration: int, SubdivisionsInBeat: int, color: str, gesturemul: float, gestureplus: float, Slack: float, Capacity: float, Stability: float, GoldenMove: bool, EnergyEvaluation: bool, TimingEvaluation: bool, CustomFloats: tuple[float]) -> None:
        super().__init__("Move")
        self.name = name
        self.CreationId = CreationId
        
        
        self.durationElement = ET.SubElement(self, "duration")
        self.duration = duration
        self.SubdivisionsInBeatElement = ET.SubElement(self, "SubdivisionsInBeat")
        self.SubdivisionsInBeat = SubdivisionsInBeat
        self.colorElement = ET.SubElement(self, "color")
        self.color = color
        self.gesturemulElement = ET.SubElement(self, "gesturemul")
        self.gesturemul = gesturemul
        self.gestureplusElement = ET.SubElement(self, "gestureplus")
        self.gestureplus = gestureplus
        self.SlackElement = ET.SubElement(self, "Slack")
        self.Slack = Slack
        self.CapacityElement = ET.SubElement(self, "Capacity")
        self.Capacity = Capacity
        self.StabilityElement = ET.SubElement(self, "Stability")
        self.Stability = Stability
        self.GoldenMoveElement = ET.SubElement(self, "GoldenMove")
        self.GoldenMove = GoldenMove
        self.EnergyEvaluationElement = ET.SubElement(self, "EnergyEvaluation")
        self.EnergyEvaluation = EnergyEvaluation
        self.TimingEvaluationElement = ET.SubElement(self, "TimingEvaluation")
        self.TimingEvaluation = TimingEvaluation
        self.CustomFloatsElement = ET.SubElement(self, "CustomFloats")
        self.CustomFloats = CustomFloats

    @property
    def name(self) -> str:
        return self.attrib["name"]

    @name.setter
    def name(self, value: str) -> None:
        self.attrib["name"] = str(value)

    @property
    def CreationId(self) -> int:
        return int(self.attrib["CreationId"])

    @CreationId.setter
    def CreationId(self, value: int) -> None:
        self.attrib["CreationId"] = str(value)

    @property
    def duration(self) -> int:
        return int(self.durationElement.text)

    @duration.setter
    def duration(self, value: int) -> None:
        self.durationElement.text = str(value)

    @property
    def SubdivisionsInBeat(self) -> int:
        return int(self.SubdivisionsInBeatElement.text)

    @SubdivisionsInBeat.setter
    def SubdivisionsInBeat(self, value: int) -> None:
        self.SubdivisionsInBeatElement.text = str(value)
    
    @property
    def color(self) -> str:
        return self.colorElement.text

    @color.setter
    def color(self, value: str) -> None:
        self.colorElement.text = str(value)

    @property
    def gesturemul(self) -> float:
        return float(self.gesturemulElement.text)

    @gesturemul.setter
    def gesturemul(self, value: float) -> None:
        self.gesturemulElement.text = str(value)

    @property
    def gestureplus(self) -> float:
        return float(self.gestureplusElement.text)

    @gestureplus.setter
    def gestureplus(self, value: float) -> None:
        self.gestureplusElement.text = str(value)

    @property
    def Slack(self) -> float:
        return float(self.SlackElement.text)

    @Slack.setter
    def Slack(self, value: float) -> None:
        self.SlackElement.text = str(value)

    @property
    def Capacity(self) -> float:
        return float(self.CapacityElement.text)

    @Capacity.setter
    def Capacity(self, value: float) -> None:
        self.CapacityElement.text = str(value)

    @property
    def Stability(self) -> float:
        return float(self.StabilityElement.text)

    @Stability.setter
    def Stability(self, value: float) -> None:
        self.StabilityElement.text = str(value)

    @property
    def GoldenMove(self) -> bool:
        return self.GoldenMoveElement.text == "True"

    @GoldenMove.setter
    def GoldenMove(self, value: bool) -> None:
        if isinstance(value, str):
            value = value == "True"
        self.GoldenMoveElement.text = str(bool(value))

    @property
    def EnergyEvaluation(self) -> bool:
        return self.EnergyEvaluationElement.text == "True"

    @EnergyEvaluation.setter
    def EnergyEvaluation(self, value: bool) -> None:
        if isinstance(value, str):
            value = value == "True"
        self.EnergyEvaluationElement.text = str(bool(value))

    @property
    def TimingEvaluation(self) -> bool:
        return self.TimingEvaluationElement.text == "True"

    @TimingEvaluation.setter
    def TimingEvaluation(self, value: float) -> None:
        if isinstance(value, str):
            value = value == "True"
        self.TimingEvaluationElement.text = str(bool(value))

    @property
    def CustomFloats(self) -> str:
        return [float(i) for i in self.CustomFloatsElement.text.split(';')]

    @CustomFloats.setter
    def CustomFloats(self, value: list[float]) -> None:
        self.CustomFloatsElement.text = ';'.join(tuple(str(i) for i in value))

class GesturesBank(ET.Element):
    def __init__(self) -> None:
        super().__init__("GesturesBank")
    
    def AddGesture(self, name: str, CreationId: int, duration: int, SubdivisionsInBeat: int, color: str, gesturemul: float, gestureplus: float, Slack: float, Capacity: float, Stability: float, GoldenMove: bool, EnergyEvaluation: bool, TimingEvaluation: bool, CustomFloats: tuple[float]) -> Gesture:
        gesture = Gesture(name, CreationId, duration, SubdivisionsInBeat, color, gesturemul, gestureplus, Slack, Capacity, Stability, GoldenMove, EnergyEvaluation, TimingEvaluation, CustomFloats)
        self.append(gesture)
        return gesture

class DataBank(ET.Element):
    PictoBank: PictoBank
    MoveBank: MoveBank
    EventsBank: EventsBank
    LyricsBank: LyricsBank
    GesturesBank: GesturesBank
    
    # To keep the order #
    MainBank: list[ET.Element]
    
    def __init__(self) -> None:
        super().__init__("databank")
        self.PictoBank = PictoBank()
        self.MoveBank = MoveBank()
        self.EventsBank = EventsBank()
        self.LyricsBank = LyricsBank()
        self.GesturesBank = GesturesBank()
        self.MainBank = []
        self.append(self.PictoBank)
        self.append(self.MoveBank)
        self.append(self.EventsBank)
        self.append(self.LyricsBank)
        self.append(self.GesturesBank)

    def AddPicto(self, name: str, CreationId: int, offset: float = None) -> Picto:
        picto = self.PictoBank.AddPicto(name, CreationId, offset)
        self.MainBank.append(picto)
        return picto
    
    def AddMove(self, name: str, CreationId: int, duration: int, SubdivisionsInBeat: int, color: str, livemovemul: float, livemoveplus: float, Slack: float, Capacity: float, Stability: float, GoldenMove: bool, EnergyEvaluation: bool, TimingEvaluation: bool, CustomFloats: tuple[float]) -> Move:
        move = self.MoveBank.AddMove(name, CreationId, duration, SubdivisionsInBeat, color, livemovemul, livemoveplus, Slack, Capacity, Stability, GoldenMove, EnergyEvaluation, TimingEvaluation, CustomFloats)
        self.MainBank.append(move)
        return move
    
    def AddEvent(self, name: str, CreationId: int, SubDivisionsInBeat: int, DefaultDuration: int) -> Event:
        event = self.EventsBank.AddEvent(name, CreationId, SubDivisionsInBeat, DefaultDuration)
        self.MainBank.append(event)
        return event
    
    def AddGesture(self, name: str, CreationId: int, duration: int, SubdivisionsInBeat: int, color: str, gesturemul: float, gestureplus: float, Slack: float, Capacity: float, Stability: float, GoldenMove: bool, EnergyEvaluation: bool, TimingEvaluation: bool, CustomFloats: tuple[float]) -> Gesture:
        gesture = self.GesturesBank.AddGesture(name, CreationId, duration, SubdivisionsInBeat, color, gesturemul, gestureplus, Slack, Capacity, Stability, GoldenMove, EnergyEvaluation, TimingEvaluation, CustomFloats)
        self.MainBank.append(gesture)
        return gesture
    
    def find(self, name: str) -> ET.Element:
        for i in self.MainBank:
            if i.name == name:
                return i
        return None

    def get(self, idx: int) -> ET.Element:
        return self.MainBank[idx].name