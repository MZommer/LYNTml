from typing import Any
import xml.etree.ElementTree as ET
class Marker(ET.Element):
    def __init__(self, position: int, name: str, sampleposition: int, date: float) -> None:
        super().__init__("marker", attrib={
            "position": str(position),
            "name": str(name),
            "sampleposition": str(sampleposition),
            "date": str(date),
        })
    
    def __str__(self) -> str:
        return f"Marker(position={self.attrib['position']}, name={self.attrib['name']}, sampleposition={self.attrib['sampleposition']}, date={self.attrib['date']})"
    
    def __repr__(self) -> str:
        return str(self)
    
class MarkerList(ET.Element):
    def __init__(self) -> None:
        super().__init__("markerlist")
    
    def AddMarker(self, position: int, name: str, sampleposition: int, date: float) -> None:
        self.append(Marker(position, name, sampleposition, date))
