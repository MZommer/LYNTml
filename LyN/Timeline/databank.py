from enum import IntEnum

from core.serializers.xml import (
    XMLAttribute,
    XMLElement,
    XMLElementCollection,
    XMLSubElement,
)


class Banks(IntEnum):
    LYRICS = 0
    PICTO = 1
    MOVE = 2
    EVENTS = 3
    # _UNK = 4
    GESTURE = 5

    @property
    def name(self) -> str:
        return super().name.capitalize()


class BankEntry(XMLElement):
    name: XMLAttribute[str]
    CreationId: XMLAttribute[int]


class Picto(BankEntry): ...


class Move(BankEntry):
    duration: XMLSubElement[float]
    SubdivisionsInBeat: XMLSubElement[int]
    color: XMLSubElement[str]  # TODO: Make type
    livemovemul: XMLSubElement[float]
    livemoveplus: XMLSubElement[float]
    Slack: XMLSubElement[float]
    Capacity: XMLSubElement[float]
    Stability: XMLSubElement[float]
    GoldenMove: XMLSubElement[bool]
    EnergyEvaluation: XMLSubElement[bool]
    TimingEvaluation: XMLSubElement[bool]
    CustomFloats: XMLSubElement[list[float]]


class Param(XMLElement):
    name: XMLAttribute[str]
    type: XMLAttribute[str]  # TODO: add resolver to dtype
    DisplayInTimeline: XMLAttribute[int]
    DefaultValue: XMLAttribute[str]


class Event(BankEntry):
    DefaultDuration: XMLSubElement[float]
    SubdivisionsInBeat: XMLSubElement[int]
    Params: XMLElementCollection[Param]


class Lyrics(BankEntry): ...


class KinectMove(BankEntry):
    duration: XMLSubElement[float]
    SubdivisionsInBeat: XMLSubElement[int]
    color: XMLSubElement[str]  # TODO: Make type
    gesturemul: XMLSubElement[float]
    gestureplus: XMLSubElement[float]
    Slack: XMLSubElement[float]
    Capacity: XMLSubElement[float]
    Stability: XMLSubElement[float]
    GoldenMove: XMLSubElement[bool]
    EnergyEvaluation: XMLSubElement[bool]
    TimingEvaluation: XMLSubElement[bool]
    # TODO: Find missing values (around 4)
    # ScoreScale
    # ScoreSmoothing
    # ScoreMode
    # Taken from UAF 2014


class DataBank(XMLElement):
    __lower_tag__ = False

    PictoBank: XMLElementCollection[Picto]
    MoveBank: XMLElementCollection[Move]
    EventsBank: XMLElementCollection[Event]
    LyricsBank: XMLElementCollection[Lyrics]
    KinectMoveBank: XMLElementCollection[KinectMove]
