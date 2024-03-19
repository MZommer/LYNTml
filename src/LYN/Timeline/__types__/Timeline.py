import xml.etree.ElementTree as ET
from .General import General
from .DataBank import DataBank
from .MarkerList import MarkerList

class Timeline(ET.Element):
    partition: ET.Element
    general: General
    databank: DataBank
    markerlist: MarkerList
    
    def __init__(self) -> None:
        super().__init__("JustDanceToolLD", attrib={
            "version": "0.0",
            "MajorVersion": "0",
            "MinorVersion": "0",
            "LastEditorUsed": "128"
        })
        self.partition = ET.SubElement(self, "partition")
        self.general = General()
        self.append(self.general)
        self.databank = DataBank()
        self.append(self.databank)
        self.markerlist = MarkerList()
        self.append(self.markerlist)
        
    def append(self, element: ET.Element) -> None:
        self.partition.append(element)
    
    def __str__(self) -> str:
        ET.indent(self, space="    ")
        return ET.tostring(self, encoding="utf-8", method="xml").decode("utf-8")
    
    def write(self, file: str) -> None:
        with open(file, "wb") as f:
            tree = ET.ElementTree(self)
            ET.indent(tree, space="    ")
            tree.write(f, encoding='utf-8', xml_declaration=True, method="xml")
    
    @property
    def version(self) -> float:
        return self._version
    
    @version.setter
    def version(self, value: float) -> None:
        self._version = value
        self.attrib["version"] = str(value)
    
    @property
    def MajorVersion(self) -> int:
        return self._MajorVersion
    
    @MajorVersion.setter
    def MajorVersion(self, value: int) -> None:
        self._MajorVersion = value
        self.attrib["MajorVersion"] = str(value)
    
    @property
    def MinorVersion(self) -> int:
        return self._MinorVersion
    
    @MinorVersion.setter
    def MinorVersion(self, value: int) -> None:
        self._MinorVersion = value
        self.attrib["MinorVersion"] = str(value)
    
    @property
    def LastEditorUsed(self) -> int:
        return self._LastEditorUsed
    
    @LastEditorUsed.setter
    def LastEditorUsed(self, value: int) -> None:
        self._LastEditorUsed = value
        self.attrib["LastEditorUsed"] = str(value)