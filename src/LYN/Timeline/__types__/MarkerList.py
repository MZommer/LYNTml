import xml.etree.ElementTree as ET


class Marker(ET.Element):
    def __init__(self, position: int, name: str, sample_position: int, date: float) -> None:
        super().__init__("marker", attrib={
            "position": str(position),
            "name": name,
            "sampleposition": str(sample_position),
            "date": str(date),
        })

    def __str__(self) -> str:
        return f"Marker(position={self.attrib['position']}, name={self.attrib['name']}, sampleposition={self.attrib['sampleposition']}, date={self.attrib['date']})"

    def __repr__(self) -> str:
        return str(self)

    @property
    def position(self) -> int:
        return int(self.attrib["position"])

    @property
    def name(self) -> str:
        return self.attrib["name"]

    @property
    def sampleposition(self) -> int:
        return int(self.attrib["sampleposition"])

    @property
    def date(self) -> float:
        return float(self.attrib["date"])


class MarkerList(ET.Element):
    def __init__(self) -> None:
        super().__init__("markerlist")

    def add_marker(self, position: int, name: str, sample_position: int, date: float) -> None:
        self.append(Marker(position, name, sample_position, date))
