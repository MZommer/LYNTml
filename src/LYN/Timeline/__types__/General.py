from collections.abc import Callable
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

class ScoreSteps(ET.Element):
    def __init__(self) -> None:
        super().__init__("ScoreSteps")
    
    def AddScoreStep(self, Name: str, Value: int) -> None:
        ET.SubElement(self, "ScoreStep", attrib={
            "Name": str(Name),
            "Value": str(Value)
        })
    
    def SetDefaultSteps(self) -> None:
        self.AddScoreStep("X", 1)
        self.AddScoreStep("Ok", 25)
        self.AddScoreStep("Good", 50)
        self.AddScoreStep("Great", 75)
        self.AddScoreStep("Perfect", 100)
    

class General(ET.Element):
    LastMoveChangeDateElement: ET.Element
    LastMoveChangeDate: str
    LastClassifierChangeDateElement: ET.Element
    LastClassifierChangeDate: str
    LastPictoModelCreateDeleteDateElement: ET.Element
    LastPictoModelCreateDeleteDate: str
    SongElement: ET.Element
    Song: str
    BeatsPerMinuteElement: ET.Element
    BeatsPerMinute: str
    SampleFrequencyElement: ET.Element
    SampleFrequency: int
    BeatsPerMeasureElement: ET.Element
    BeatsPerMeasure: int
    FirstMeasureMarkerPosElement: ET.Element
    FirstMeasureMarkerPos: int
    WaveNbSamplesElement: ET.Element
    WaveNbSamples: ET.Element
    WavePathElement: ET.Element
    WavePath: str
    VideoPathElement: ET.Element
    VideoPath: str
    PictoFolderElement: ET.Element
    PictoFolder: str
    CustomScoreStepsElement: ET.Element
    CustomScoreSteps: bool
    ScoreSteps: ScoreSteps
    
    
    def __init__(self) -> None:
        super().__init__("general")
        self.LastClassifierChangeDateElement = ET.SubElement(self, "LastClassifierChangeDate")
        self.LastMoveChangeDateElement = ET.SubElement(self, "LastMoveChangeDate")
        self.LastPictoModelCreateDeleteDateElement = ET.SubElement(self, "LastPictoModelCreateDeleteDate")
        self.SongElement = ET.SubElement(self, "Song")
        self.BeatsPerMinuteElement = ET.SubElement(self, "BeatsPerMinute")
        self.SampleFrequencyElement = ET.SubElement(self, "SampleFrequency")
        self.BeatsPerMeasureElement = ET.SubElement(self, "BeatsPerMeasure")
        self.FirstMeasureMarkerPosElement = ET.SubElement(self, "FirstMeasureMarkerPos")
        self.WaveNbSamplesElement = ET.SubElement(self, "WaveNbSamples")
        self.WavePathElement = ET.SubElement(self, "WavePath")
        self.VideoPathElement = ET.SubElement(self, "VideoPath")
        self.PictoFolderElement = ET.SubElement(self, "PictoFolder")
        self.CustomScoreStepsElement = ET.SubElement(self, "CustomScoreSteps")
        self.ScoreSteps = ScoreSteps()
        self.append(self.ScoreSteps)
    
    @property
    def LastClassifierChangeDate(self) -> str:
        return self.LastClassifierChangeDateElement.text
    @LastClassifierChangeDate.setter
    def LastClassifierChangeDate(self, value: str) -> None:
        self.LastClassifierChangeDateElement.text = str(value)
    
    @property
    def LastMoveChangeDate(self) -> str:
        return self.LastMoveChangeDateElement.text
    @LastMoveChangeDate.setter
    def LastMoveChangeDate(self, value: str) -> None:
        self.LastMoveChangeDateElement.text = str(value)
    
    @property
    def LastPictoModelCreateDeleteDate(self) -> str:
        return self.LastPictoModelCreateDeleteDateElement.text
    @LastPictoModelCreateDeleteDate.setter
    def LastPictoModelCreateDeleteDate(self, value: str) -> None:
        self.LastPictoModelCreateDeleteDateElement.text = str(value)
        
    @property
    def Song(self) -> str:
        return self.SongElement.text
    @Song.setter
    def Song(self, value: str) -> None:
        self.SongElement.text = str(value)
    
    @property
    def BeatsPerMinute(self) -> int:
        return self._BeatsPerMinute
    @BeatsPerMinute.setter
    def BeatsPerMinute(self, value: int) -> None:
        self._BeatsPerMinute = value
        self.BeatsPerMinuteElement.text = str(value)
    
    @property
    def SampleFrequency(self) -> int:
        return self._SampleFrequency
    @SampleFrequency.setter
    def SampleFrequency(self, value: int) -> None:
        self._SampleFrequency = value
        self.SampleFrequencyElement.text = str(value)
    
    @property
    def BeatsPerMeasure(self) -> int:
        return self._BeatsPerMeasure
    @BeatsPerMeasure.setter
    def BeatsPerMeasure(self, value: int) -> None:
        self._BeatsPerMeasure = value
        self.BeatsPerMeasureElement.text = str(value)
    
    @property
    def FirstMeasureMarkerPos(self) -> int:
        return self._FirstMeasureMarkerPos
    @FirstMeasureMarkerPos.setter
    def FirstMeasureMarkerPos(self, value: int) -> None:
        self._FirstMeasureMarkerPos = value
        self.FirstMeasureMarkerPosElement.text = str(value)
    
    @property
    def WaveNbSamples(self) -> int:
        return self._WaveNbSamples
    @WaveNbSamples.setter
    def WaveNbSamples(self, value: int) -> None:
        self._WaveNbSamples = value
        self.WaveNbSamplesElement.text = str(value)
        
    @property
    def WavePath(self) -> str:
        return self.WavePathElement.text
    @WavePath.setter
    def WavePath(self, value: str) -> None:
        self.WavePathElement.text = str(value)
        
    @property
    def VideoPath(self) -> str:
        return self.VideoPathElement.text
    @VideoPath.setter
    def VideoPath(self, value: str) -> None:
        self.VideoPathElement.text = str(value)
    
    @property
    def PictoFolder(self) -> str:
        return self.PictoFolderElement.text
    @PictoFolder.setter
    def PictoFolder(self, value: str) -> None:
        self.PictoFolderElement.text = str(value)
    
    @property
    def CustomScoreSteps(self) -> bool:
        return self._CustomScoreSteps
    @CustomScoreSteps.setter
    def CustomScoreSteps(self, value: bool) -> None:
        self._CustomScoreSteps = value
        self.CustomScoreStepsElement.text = str(value)
