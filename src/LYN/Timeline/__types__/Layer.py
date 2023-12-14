import xml.etree.ElementTree as ET

class Instance(ET.Element):
    position: int
    model: str
    ## Not in the XML but serialized ##
    date: float
    
    def __init__(self, position: int, model: str, date: float = None) -> None:
        super().__init__("Instance")
        self.position = position
        self.model = model
        if date is not None:
            self.date = date
    
    def __str__(self) -> str:
        return f"Instance: {self.position} {self.model}"
    
    def __repr__(self) -> str:
        return str(self)
    
    @property
    def position(self) -> int:
        return self._position
    
    @position.setter
    def position(self, value: int) -> None:
        self._position = value
        self.attrib["position"] = str(value)
    
    @property
    def model(self) -> str:
        return self._model
    @model.setter
    def model(self, value: str) -> None:
        self._model = value
        self.attrib["model"] = str(value)
    
    @property
    def date(self) -> float:
        return self._date
    @date.setter
    def date(self, value: float) -> None:
        self._date = value
        self.attrib["date"] = str(value)

class Layer(ET.Element):
    name: str
    type: str
    position: int
    
    def __init__(self, name: str, type: str, position: int) -> None:
        super().__init__("Layer", attrib={
            "name": name,
            "type": type,
            "position": str(position)
        })
        self.name = name
        self.type = type
        self.position = position
        # Inmutable, not adding protectors
        
class PictoLayer(Layer):
    def AddInstance(self, position: int, model: str, date: float = None) -> Instance:
        instance = Instance(position, model, date)
        self.append(instance)
        return instance

class MoveInstance(Instance):
    OffsetInSubdivisionsElement: ET.Element
    OffsetInSubdivisions: int
    GoldMoveElement: ET.Element
    GoldMove: bool
    
    def __init__(self, position: int, model: str, date: float, duration: float, GoldMove: bool, OffsetInSubdivisions: int) -> None:
        super().__init__(position, model, date)
        self.duration = duration
        self.OffsetInSubdivisionsElement = ET.SubElement(self, "OffsetInSubdivisions")
        self.OffsetInSubdivisions = OffsetInSubdivisions
        if GoldMove:
            self.GoldMoveElement = ET.SubElement(self, "GoldMove")
            self.GoldMove = GoldMove
    
    @property
    def duration(self) -> float:
        return self._duration
    @duration.setter
    def duration(self, value: float) -> None:
        self._duration = value
        self.attrib["duration"] = str(value)
    
    @property
    def OffsetInSubdivisions(self) -> int:
        return self._OffsetInSubdivisions
    @OffsetInSubdivisions.setter
    def OffsetInSubdivisions(self, value: int) -> None:
        self._OffsetInSubdivisions = value
        self.OffsetInSubdivisionsElement.text = str(value)
    
    @property
    def GoldMove(self) -> bool:
        return self._GoldMove
    @GoldMove.setter
    def GoldMove(self, value: bool) -> None:
        if isinstance(value, str):
            value = value.lower() == "true"
        elif not isinstance(value, bool):
            value = bool(value)
        self._GoldMove = value
        self.GoldMoveElement.text = str(value)

class MoveLayer(Layer):
    def AddInstance(self, position: int, model: str, date: float, duration: float, GoldMove: bool, OffsetInSubdivisions: int) -> Instance:
        instance = MoveInstance(position, model, date, duration, GoldMove, OffsetInSubdivisions)
        self.append(instance)
        return instance

class LyricsInstance(Instance):
        OffsetElement: ET.Element
        Offset: float
        LengthElement: ET.Element
        Length: float
        TextElement: ET.Element
        Text: str
        
        def __init__(self, position: int, model: str, Offset: float, Length: float, Text: str) -> None:
            super().__init__(position, model)
            self.OffsetElement = ET.SubElement(self, "Offset")
            self.Offset = Offset
            self.LengthElement = ET.SubElement(self, "Length")
            self.Length = Length
            self.TextElement = ET.SubElement(self, "Text")
            self.Text = Text
        
        @property
        def Offset(self) -> float:
            return self._Offset
        @Offset.setter
        def Offset(self, value: float) -> None:
            self._Offset = value
            self.OffsetElement.text = str(value)
        
        @property
        def Length(self) -> float:
            return self._Length
        @Length.setter
        def Length(self, value: float) -> None:
            self._Length = value
            self.LengthElement.text = str(value)
        
        @property
        def Text(self) -> str:
            return self._Text
        @Text.setter
        def Text(self, value: str) -> None:
            self._Text = value
            self.TextElement.text = str(value)     

class LyricsLayer(Layer):
    def AddInstance(self, position: int, model: str, offset: float, length: float, text: str) -> Instance:
        instance = LyricsInstance(position, model, offset, length, text)
        self.append(instance)
        return instance

class EventInstance(Instance):
    class Param(ET.Element):
        name: str
        value: any
        
        def __init__(self, name: str, value: any) -> None:
            super().__init__("Param")
            self.name = name
            self.value = value
        
        @property
        def name(self) -> str:
            return self.attrib["name"]
        @name.setter
        def name(self, value: str) -> None:
            self.attrib["name"] = value
        
        @property
        def value(self) -> any:
            return self.attrib["value"]
        @value.setter
        def value(self, value: any) -> None:
            self.attrib["value"] = str(value)        
    
    OffsetElement: ET.Element
    Offset: float
    LengthElement: ET.Element
    Length: float
    colorElement: ET.Element
    color: str
    Params: ET.Element
    
    def __init__(self, position: int, model: str, Offset: float, Length: float, color: str) -> None:
        super().__init__(position, model)
        self.OffsetElement = ET.SubElement(self, "Offset")
        self.Offset = Offset
        self.LengthElement = ET.SubElement(self, "Length")
        self.Length = Length
        self.colorElement = ET.SubElement(self, "color")
        self.color = color
        self.Params = ET.SubElement(self, "Params")
        
    def AddParam(self, name: str, value: str) -> None:
        param = EventInstance.Param(name, value)
        self.Params.append(param)
    
    @property
    def Offset(self) -> float:
        return self._Offset
    @Offset.setter
    def Offset(self, value: float) -> None:
        self._Offset = value
        self.OffsetElement.text = str(value)
    
    @property
    def Length(self) -> float:
        return self._Length
    @Length.setter
    def Length(self, value: float) -> None:
        self._Length = value
        self.LengthElement.text = str(value)
    
    @property
    def color(self) -> str:
        return self.colorElement.text
    @color.setter
    def color(self, value: str) -> None:
        self.colorElement.text = str(value)     

class EventLayer(Layer):
    def AddInstance(self, position: int, model: str, Offset: float, Length: float, color: str) -> Instance:
        instance = EventInstance(position, model, Offset, Length, color)
        self.append(instance)
        return instance