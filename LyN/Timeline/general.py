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
    WavePath: XMLSubElement[str]
    VideoPath: XMLSubElement[str]
    PictoFolder: XMLSubElement[str]
    CustomScoreSteps: XMLSubElement[bool]
    ScoreSteps: XMLElementCollection[ScoreStep] = (
        ScoreStep(name="X", value=1),
        ScoreStep(name="Ok", value=25),
        ScoreStep(name="Good", value=50),
        ScoreStep(name="Great", value=75),
        ScoreStep(name="Perfect", value=100),
    )
