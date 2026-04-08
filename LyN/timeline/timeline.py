from core.serializers.xml import (
    XMLAttribute,
    XMLElement,
    XMLElementCollection,
    XMLSiblingCollection,
)

from .databank import DataBank
from .general import General
from .layer import Layer
from .markerlist import Marker


class Partition(XMLElement):
    __lower_tag__ = False

    general: General
    databank: DataBank
    markerlist: XMLElementCollection[Marker]
    layers: XMLSiblingCollection[Layer]


class JustDanceToolLD(XMLElement):
    partition: Partition

    version: XMLAttribute[float] = 15.0
    MajorVersion: XMLAttribute[float] = 0.0
    MinorVersion: XMLAttribute[float] = 0.0
    LastEditorUsed: XMLAttribute[float] = 128.0
