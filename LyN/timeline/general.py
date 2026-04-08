from core.serializers.xml import (
    XMLAttribute,
    XMLElement,
    XMLElementCollection,
    XMLSubElement,
)


class ScoreStep(XMLElement):
    Name: XMLAttribute[str]
    Value: XMLAttribute[int]


class General(XMLElement):
    __lower_tag__ = False

    LastClassifierChangeDate: XMLSubElement[str]
    LastMoveChangeDate: XMLSubElement[str]
    LastPictoModelCreateDeleteDate: XMLSubElement[str]
    Song: XMLSubElement[str]
    BeatsPerMinute: XMLSubElement[int]
    SampleFrequency: XMLSubElement[int]
    BeatsPerMeasure: XMLSubElement[int]
    FirstMeasureMarkerPos: XMLSubElement[int]
    WaveNbSamples: XMLSubElement[int]
    CustomScoreSteps: XMLSubElement[bool]
    WavePath: XMLSubElement[str] = r".\Sounds\{Song}.wav"
    VideoPath: XMLSubElement[str] = r"\{Song}\Videos\{Song}.bik"
    PictoFolder: XMLSubElement[str] = r".\Pictos"
    ScoreSteps: XMLElementCollection[ScoreStep] = (
        ScoreStep(Name="X", Value=1),
        ScoreStep(Name="Ok", Value=25),
        ScoreStep(Name="Good", Value=50),
        ScoreStep(Name="Great", Value=75),
        ScoreStep(Name="Perfect", Value=100),
    )
