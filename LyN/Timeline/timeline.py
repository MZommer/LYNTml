from core.serializers.xml import (
    XMLAttribute,
    XMLElement,
    XMLElementCollection,
    XMLSiblingCollection,
)

from .general import General
from .layer import Layer
from .markerlist import Marker


class Partition(XMLElement):
    __lower_tag__ = False

    general: General
    markerlist: XMLElementCollection[Marker]
    layers: XMLSiblingCollection[Layer]


class JustDanceToolLD(XMLElement):
    version: XMLAttribute[int] = 15
    MajorVersion: XMLAttribute[int] = 0
    MinorVersion: XMLAttribute[int] = 0
    LastEditorUsed: XMLAttribute[int] = 128

    partition: Partition
