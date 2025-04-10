import xml.etree.ElementTree as ET

from .__types__ import (
    Timeline,
    PictoLayer, MoveLayer, LyricsLayer, EventLayer, EventInstance,
)


def tree2dict(tree: ET.Element) -> dict:
    def element2dict(element: ET.Element) -> dict:
        result = {}
        if element.text:
            result[element.tag] = element.text
        if element.attrib:
            result.update(element.attrib)
        if tuple(element):  # TODO: check if len(element)
            result[element.tag] = [element2dict(child) for child in element]
        return result

    result = {}
    result.update(tree.attrib)
    for element in tree:
        result.update(element2dict(element))
    return result


class XMLSerializer:
    # Timeline: Timeline
    tree: ET.ElementTree

    def __init__(self) -> None:
        self.timeline = Timeline()

    def deserialize(self, path: str) -> Timeline:
        tree = ET.parse(path)
        root = tree.getroot().find("partition")

        for element in root:
            if element.tag == "general":
                self._load_general(element)
            elif element.tag == "databank":
                self._load_banks(element)
            elif element.tag == "markerlist":
                self._load_markerlist(element)
            elif element.tag == "layer":
                self._load_layer(element)
            else:
                raise Exception(f"Unknown element tag: {element.tag}")

        return self.timeline

    def _load_general(self, element: ET.Element) -> None:
        general = self.timeline.general
        for child in element:
            if child.tag == "ScoreSteps":
                for score_step in child:
                    general.ScoreSteps.add_score_step(
                        score_step.attrib["Name"],
                        int(score_step.attrib["Value"]),
                    )
            else:
                setattr(general, child.tag, child.text)

    def _load_banks(self, element: ET.Element) -> None:
        for child in element:
            if child.tag == "PictoBank":
                self._load_picto_bank(child)
            elif child.tag == "MoveBank":
                self._load_move_bank(child)
            elif child.tag == "EventsBank":
                self._load_events_bank(child)
            elif child.tag == "LyricsBank":
                pass
            elif child.tag == "GestureBank":
                pass
            else:
                raise Exception(f"Unknown bank: {child.tag}")

    def _load_picto_bank(self, element: ET.Element) -> None:
        picto_bank = self.timeline.databank.PictoBank
        for child in element:
            picto_bank.add_picto(
                child.attrib["name"],
                int(child.attrib["CreationId"]),
                child.attrib.get("duration"),
            )

    def _load_move_bank(self, element: ET.Element) -> None:
        move_bank = self.timeline.databank.MoveBank
        for child in element:
            doc = tree2dict(child)
            move_bank.add_move(
                doc["name"], doc["CreationId"],
                doc["duration"], doc["SubdivisionsInBeat"], doc["color"],
                doc["livemovemul"], doc["livemoveplus"], doc["Slack"], doc["Capacity"], doc["Stability"],
                doc["GoldenMove"], doc["EnergyEvaluation"], doc["TimingEvaluation"],
                doc["CustomFloats"],
            )

    def _load_events_bank(self, element: ET.Element) -> None:
        events_bank = self.timeline.databank.EventsBank
        for child in element:
            name = child.attrib["name"]
            creation_id = child.attrib["CreationId"]
            default_duration = child.find("DefaultDuration").text
            subdivisions_in_beat = child.find("SubdivisionsInBeat").text
            event = events_bank.add_event(
                name,
                int(creation_id),
                int(default_duration),
                int(subdivisions_in_beat),
            )
            for param in child.find("Params"):
                event.add_param(
                    param.attrib["name"],
                    param.attrib["type"],
                    int(param.attrib["DisplayInTimeline"]),
                    param.attrib["DefaultValue"],
                )

    def _load_markerlist(self, element: ET.Element) -> None:
        markerlist = self.timeline.markerlist
        for marker in element:
            markerlist.add_marker(
                int(marker.attrib["position"]),
                marker.attrib["name"],
                int(marker.attrib["sampleposition"]),
                float(marker.attrib["date"]),
            )

    def _load_layer(self, element: ET.Element) -> None:
        if element.attrib["type"] == "Picto":
            self._load_picto_layer(element)
        elif element.attrib["type"] == "Move":
            self._load_move_layer(element)
        elif element.attrib["type"] == "Lyrics":
            self._load_lyrics_layer(element)
        elif element.attrib["type"] == "Events":
            self._load_events_layer(element)

    def _load_picto_layer(self, element: ET.Element) -> None:
        layer = PictoLayer(
            element.attrib["name"],
            element.attrib["type"],
            int(element.attrib["position"]),
        )
        self.timeline.append(layer)
        for child in element:
            if child.tag == "Instance":
                layer.AddInstance(
                    int(child.attrib["position"]),
                    child.attrib["model"],
                    float(child.attrib["date"]),
                )

    def _load_move_layer(self, element: ET.Element) -> None:
        layer = MoveLayer(
            element.attrib["name"],
            element.attrib["type"],
            int(element.attrib["position"]),
        )
        self.timeline.append(layer)
        for child in element:
            if child.tag == "Instance":
                gold_move = child.find("GoldMove").text
                offset_in_subdivisions = child.find("OffsetInSubdivisions").text
                layer.AddInstance(
                    int(child.attrib["position"]),
                    child.attrib["model"],
                    float(child.attrib["date"]),
                    float(child.attrib["duration"]),
                    bool(gold_move),
                    int(offset_in_subdivisions),
                )

    def _load_lyrics_layer(self, element: ET.Element) -> None:
        layer = LyricsLayer(
            element.attrib["name"],
            element.attrib["type"],
            int(element.attrib["position"]),
        )
        self.timeline.append(layer)
        for child in element:
            if child.tag == "Instance" and child.attrib["model"] == "Lyrics":
                offset = child.find("Offset").text
                length = child.find("Length").text
                text = child.find("Text").text
                layer.AddInstance(
                    int(child.attrib["position"]),
                    child.attrib["model"],
                    float(offset),
                    float(length),
                    text,
                )

    def _load_events_layer(self, element: ET.Element) -> None:
        layer = EventLayer(
            element.attrib["name"],
            element.attrib["type"],
            int(element.attrib["position"]),
        )
        self.timeline.append(layer)
        for child in element:
            if child.tag == "Instance":
                offset = child.find("Offset").text
                length = child.find("Length").text
                color = child.find("color").text
                params = child.find("Params")
                instance: EventInstance = layer.AddInstance(
                    int(child.attrib["position"]),
                    child.attrib["model"],
                    float(offset),
                    float(length),
                    color,
                )

                for param in params:
                    instance.AddParam(param.attrib["name"], param.attrib["value"])
