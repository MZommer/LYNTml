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
    EVENT = 3
    SEQUENCE = 4
    KINECTMOVE = 5  # Or Storyboard in legacy

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
    CustomInts: XMLSubElement[list[int]]


class Param(XMLElement):
    name: XMLAttribute[str]
    type: XMLAttribute[str]  # TODO: add resolver to dtype
    DisplayInTimeline: XMLAttribute[int]
    DefaultValue: XMLAttribute[str]


class Event(BankEntry):
    DefaultDuration: XMLSubElement[int]
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
    CustomFloats: XMLSubElement[list[float]]
    CustomInts: XMLSubElement[list[int]]
    ScoreOffset: XMLSubElement[float]
    ScoreScale: XMLSubElement[float]
    ScoreSmooth: XMLSubElement[float]
    ScoringMode: XMLSubElement[int]


class DataBank(XMLElement):
    __lower_tag__ = False

    PictoBank: XMLElementCollection[Picto]
    MoveBank: XMLElementCollection[Move]
    EventsBank: XMLElementCollection[Event]
    LyricsBank: XMLElementCollection[Lyrics]
    KinectMoveBank: XMLElementCollection[KinectMove]

    def add_entry(self, entry: Picto | Move | Event | KinectMove) -> None:
        if isinstance(entry, Picto):
            self.PictoBank.append(entry)
        elif isinstance(entry, Move):
            self.MoveBank.append(entry)
        elif isinstance(entry, Event):
            self.EventsBank.append(entry)
        elif isinstance(entry, KinectMove):
            self.KinectMoveBank.append(entry)
        else:
            raise ValueError(f"Unknown data bank entry of type {type(entry)}")
