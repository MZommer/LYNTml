from enum import StrEnum

from core.serializers.xml import (
    XMLAttribute,
    XMLElement,
    XMLElementCollection,
    XMLSiblingCollection,
    XMLSubElement,
)


class LayerType(StrEnum):
    EVENTS = "Events"
    PICTO = "Picto"
    MOVE = "Move"
    LYRICS = "Lyrics"


class Instance(XMLElement):
    position: XMLAttribute[int]  # Not serialized in Binary
    model: XMLAttribute[str]
    date: XMLAttribute[float]  # Not serialized in XML (calculated through the position)

    @property
    def tag(self) -> str:
        return "Instance"


class Layer(XMLElement):
    name: XMLAttribute[str]
    type: XMLAttribute[LayerType]
    position: XMLAttribute[int]

    instances: XMLSiblingCollection[Instance]

    @property
    def tag(self) -> str:
        return "Layer"


class PictoLayer(Layer):
    type: XMLAttribute[LayerType] = LayerType.PICTO


class MoveInstance(Instance):
    duration: XMLAttribute[float]
    OffsetInSubdivisions: XMLSubElement[int]


class MoveLayer(Layer):
    type: XMLAttribute[LayerType] = LayerType.MOVE
    instances: XMLSiblingCollection[MoveInstance]


class LyricsInstance(Instance):
    Offset: XMLSubElement[float]
    Length: XMLSubElement[float]
    Text: XMLSubElement[str]


class LyricsLayer(Layer):
    type: XMLAttribute[LayerType] = LayerType.LYRICS
    instances: XMLSiblingCollection[LyricsInstance]


class Param(XMLElement):
    name: XMLAttribute[str]
    value: XMLAttribute[str]


class EventInstance(Instance):
    Offset: XMLSubElement[float]
    Length: XMLSubElement[float]
    color: XMLSubElement[str]  # TODO: Make type
    Params: XMLElementCollection[Param]


class EventsLayer(Layer):
    type: XMLAttribute[LayerType] = LayerType.EVENTS
    instances: XMLSiblingCollection[EventInstance]
