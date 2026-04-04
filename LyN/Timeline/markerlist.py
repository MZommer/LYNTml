from core.serializers.xml import XMLAttribute, XMLElement


class Marker(XMLElement):
    __lower_tag__ = False

    position: XMLAttribute[int]
    name: XMLAttribute[str]
    sampleposition: XMLAttribute[int]
    date: XMLAttribute[float]
