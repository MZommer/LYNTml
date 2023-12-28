import xml.etree.ElementTree as ET
from .__types__ import (
    Timeline,
    PictoLayer, MoveLayer, LyricsLayer, EventLayer,
)

def tree2dict(tree: ET.Element) -> dict:
    def element2dict(element: ET.Element) -> dict:
        result = {}
        if element.text:
            result[element.tag] = element.text
        if element.attrib:
            result.update(element.attrib)
        if tuple(element):
            result[element.tag] = [element2dict(child) for child in element]
        return result
    result = {}
    result.update(tree.attrib)
    for element in tree:
        result.update(element2dict(element))
    return result

class XMLSerializer:
    Timeline: Timeline
    tree: ET.ElementTree
    def __init__(self) -> None:
        self.Timeline = Timeline()
        
    
    def Deserialize(self, path: str) -> Timeline:
        tree = ET.parse(path)
        root = tree.getroot().find("partition")
        
        for element in root:
            if element.tag == "general":
                self.__loadGeneral(element)
            elif element.tag == "databank":
                self.__loadBanks(element)
            elif element.tag == "markerlist":
                self.__loadMarkerlist(element)
            elif element.tag == "layer":
                self.__loadLayer(element)
            else:
                raise Exception(f"Unknown element tag: {element.tag}")
        
        return self.Timeline
        
    
    def __loadGeneral(self, element: ET.Element) -> None:
        general = self.Timeline.general
        for child in element:
            if child.tag == "ScoreSteps":
                for scorestep in child:
                    general.ScoreSteps.AddScoreStep(scorestep.attrib["Name"], int(scorestep.attrib["Value"]))
            else:
                setattr(general, child.tag, child.text)
    
    def __loadBanks(self, element: ET.Element) -> None:
        for child in element:
            if child.tag == "PictoBank":
                self.__loadPictoBank(child)
            elif child.tag == "MoveBank":
                self.__loadMoveBank(child)
            elif child.tag == "EventsBank":
                self.__loadEventsBank(child)
            elif child.tag == "LyricsBank":
                pass
            elif child.tag == "GesturesBank":
                pass
            else:
                raise Exception(f"Unknown bank: {child.tag}")
    
    def __loadPictoBank(self, element: ET.Element) -> None:
        PictoBank = self.Timeline.databank.PictoBank
        for child in element:
            PictoBank.AddPicto(child.attrib["name"], child.attrib["CreationId"], child.attrib.get("duration"))
    
    def __loadMoveBank(self, element: ET.Element) -> None:
        MoveBank = self.Timeline.databank.MoveBank
        for child in element:
            doc = tree2dict(child)
            MoveBank.AddMove(
                doc["name"], doc["CreationId"],
                doc["duration"], doc["SubdivisionsInBeat"], doc["color"],
                doc["livemovemul"], doc["livemoveplus"], doc["Slack"], doc["Capacity"], doc["Stability"],
                doc["GoldenMove"], doc["EnergyEvaluation"], doc["TimingEvaluation"],
                doc["CustomFloats"]                
            )
    
    def __loadEventsBank(self, element: ET.Element) -> None:
        EventsBank = self.Timeline.databank.EventsBank
        for child in element:
            name = child.attrib["name"]
            CreationId = child.attrib["CreationId"]
            DefaultDuration = child.find("DefaultDuration").text
            SubdivisionsInBeat = child.find("SubdivisionsInBeat").text
            event = EventsBank.AddEvent(name, CreationId, DefaultDuration, SubdivisionsInBeat)
            Params = child.find("Params")
            for param in Params:
                event.AddParam(param.attrib["name"], param.attrib["type"], param.attrib["DisplayInTimeline"], param.attrib["DefaultValue"])
    
    def __loadMarkerlist(self, element: ET.Element) -> None:
        markerlist = self.Timeline.markerlist
        for marker in element:
            markerlist.AddMarker(marker.attrib["position"], marker.attrib["name"], marker.attrib["sampleposition"], marker.attrib["date"])
    
    def __loadLayer(self, element: ET.Element) -> None:
        if element.attrib["type"] == "Picto":
            self.__loadPictoLayer(element)
        elif element.attrib["type"] == "Move":
            self.__loadMoveLayer(element)
        elif element.attrib["type"] == "Lyrics":
            self.__loadLyricsLayer(element)
        elif element.attrib["type"] == "Events":
            self.__loadEventsLayer(element)
    
    def __loadPictoLayer(self, element: ET.Element) -> None:
        layer = PictoLayer(element.attrib["name"], element.attrib["type"], element.attrib["position"])
        self.Timeline.append(layer)
        for child in element:
            if child.tag == "Instance":
                layer.AddInstance(child.attrib["position"], child.attrib["model"], child.attrib["date"])
    
    def __loadMoveLayer(self, element: ET.Element) -> None:
        layer = MoveLayer(element.attrib["name"], element.attrib["type"], element.attrib["position"])
        self.Timeline.append(layer)
        for child in element:
            if child.tag == "Instance":
                GoldMove = child.find("GoldMove").text
                OffsetInSubdivisions = child.find("OffsetInSubdivisions").text
                layer.AddInstance(child.attrib["position"], child.attrib["model"], child.attrib["date"], child.attrib["duration"], GoldMove, OffsetInSubdivisions)
    
    def __loadLyricsLayer(self, element: ET.Element) -> None:
        layer = LyricsLayer(element.attrib["name"], element.attrib["type"], element.attrib["position"])
        self.Timeline.append(layer)
        for child in element:
            if child.tag == "Instance" and child.attrib["model"] == "Lyrics":
                Offset = child.find("Offset").text
                Length = child.find("Length").text
                Text = child.find("Text").text
                layer.AddInstance(child.attrib["position"], child.attrib["model"], Offset, Length, Text)
    
    def __loadEventsLayer(self, element: ET.Element) -> None:
        layer = EventLayer(element.attrib["name"], element.attrib["type"], element.attrib["position"])
        self.Timeline.append(layer)
        for child in element:
            if child.tag == "Instance":
                Offset = child.find("Offset").text
                Length = child.find("Length").text
                color = child.find("color").text
                Params = child.find("Params")
                instance = layer.AddInstance(child.attrib["position"], child.attrib["model"], Offset, Length, color)
                
                for param in Params:
                    instance.AddParam(param.attrib["name"], param.attrib["value"])
    