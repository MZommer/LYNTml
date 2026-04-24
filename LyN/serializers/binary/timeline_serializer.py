import datetime
from io import BytesIO
from itertools import chain
from typing import BinaryIO

from core.logger import logger
from core.serializers.binary import BinaryReader, ByteOrder
from LyN.serializers.binary.helpers import lyn_struct
from LyN.timeline.databank import (
    PARAM_TO_TYPE,
    Banks,
    DataBank,
    Event,
    KinectMove,
    Move,
    ParamType,
    Picto,
)
from LyN.timeline.databank import (
    Param as BankParam,
)
from LyN.timeline.general import General, ScoreStep
from LyN.timeline.layer import (
    EventInstance,
    EventsLayer,
    Instance,
    Layer,
    LyricsInstance,
    LyricsLayer,
    MoveInstance,
    MoveLayer,
    PictoLayer,
)
from LyN.timeline.layer import (
    Param as InstanceParam,
)
from LyN.timeline.markerlist import Marker
from LyN.timeline.timeline import JustDanceToolLD, Partition

LEGACY_VERSION = 9


class TimelineSerializer:
    _reader: BinaryReader
    version: int

    def __init__(self) -> None:
        self.beats: tuple[float, ...] = ()

    def deserialize(self, stream: BinaryIO | bytes) -> JustDanceToolLD:
        if isinstance(stream, bytes):
            stream = BytesIO(stream)
        self._reader = BinaryReader(ByteOrder.LITTLE, stream)
        return self._deserialize_timeline()

    # Helper functions #
    def get_virtual_position(self, time: float) -> tuple[int, float]:
        if not self.beats:
            return 0, time
        position = self.beats.index(min(self.beats, key=lambda item: abs(item - time)))
        offset = time - self.beats[position]
        return position, offset

    @property
    def legacy(self) -> bool:
        return self.version < LEGACY_VERSION

    # Reader functions #
    @lyn_struct
    def _deserialize_timeline(self) -> JustDanceToolLD:
        logger.debug("Deserializing timeline")
        general = self._deserialize_general()
        markers = self._deserialize_markers()
        databank = self._deserialize_data_bank()
        layers = self._deserialize_layers(databank=databank)
        return JustDanceToolLD(
            version=self.version,
            partition=Partition(
                general=general,
                databank=databank,
                markerlist=markers,
                layers=layers,
            ),
        )

    @lyn_struct
    def _deserialize_general(self) -> General:
        date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.version = self._reader.float()
        song = self._reader.string8()
        general = General(
            Song=song,
            BeatsPerMeasure=self._reader.uint32(),
            FirstMeasureMarkerPos=self._reader.uint32(),
            BeatsPerMinute=self._reader.uint32(),
            SampleFrequency=self._reader.uint32(),
            WaveNbSamples=self._reader.uint32(),
            CustomScoreSteps=bool(self._reader.uint32()),
            ScoreSteps=[
                ScoreStep(
                    Name=self._reader.string8(),
                    Value=self._reader.uint32(),
                )
                for _ in range(self._reader.uint32())
            ],
            WavePath=rf".\Sounds\{song}.wav",
            VideoPath=rf".\{song}\Videos\{song}.bik",
            PictoFolder=r".\Pictos",
            LastMoveChangeDate=date,
            LastClassifierChangeDate=date,
            LastPictoModelCreateDeleteDate=date,
        )
        logger.debug(f"Deserializing GENERAL {self.version=} {self.legacy=}")
        if not self.legacy:
            # 4 uint16 values ? sometimes with values and sometimes 00 00
            # TODO: Investigate this values, probably some ids
            self._reader.array(self._reader.ushort, 4)
        general.LastMoveChangeDate = self._reader.date().strftime("%d/%m/%Y %H:%M:%S")
        general.LastClassifierChangeDate = self._reader.date().strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        return general

    @lyn_struct
    def _deserialize_markers(self) -> tuple[Marker, ...]:
        logger.debug("Deserializing MARKERS")
        self._reader.uint32()  # 0x00
        markers = tuple(
            Marker(
                position=position,
                sampleposition=self._reader.float(),
                date=self._reader.float(),
                name=self._reader.string8(),
            )
            for position in range(self._reader.uint32())
        )
        self.beats = tuple(marker.date for marker in markers)
        return markers

    @lyn_struct
    def _deserialize_data_bank(self) -> DataBank:
        databank = DataBank()
        for creation_id in range(self._reader.uint32()):
            entry = self._deserialize_bank(creation_id)
            databank.add_entry(entry)
        return databank

    @lyn_struct(trustable=True)
    def _deserialize_bank(self, creation_id: int) -> Picto | Move | Event | KinectMove:
        bank = self._reader.uint32()
        name = self._reader.string8()
        logger.debug(f"Deserializing BANK {name} ({Banks(bank).name})")
        if bank == Banks.LYRICS:
            logger.warning("LYRICS BANK?")
        elif bank == Banks.PICTO:
            return Picto(
                name=name,
                CreationId=creation_id,
            )
        elif bank == Banks.MOVE:
            return Move(
                name=name,
                CreationId=creation_id,
                duration=2.0,
                SubdivisionsInBeat=2,
                color="0x00000000",  # Not serialized data?
                livemovemul=self._reader.float(),
                livemoveplus=self._reader.float(),
                Slack=self._reader.float(),
                Capacity=self._reader.float(),
                Stability=self._reader.float(),
                GoldenMove=bool(self._reader.uint32()),
                EnergyEvaluation=bool(self._reader.uint32()),
                TimingEvaluation=bool(self._reader.uint32()),
                CustomFloats=self._reader.vector(),
                CustomInts=self._reader.array(
                    self._reader.uint32
                ),  # TODO: Check int size
            )
        elif bank == Banks.KINECTMOVE:
            return KinectMove(
                name=name,
                CreationId=creation_id,
                duration=2.0,
                SubdivisionsInBeat=2,
                color="0x00000000",  # Not serialized data?
                gesturemul=self._reader.float(),
                gestureplus=self._reader.float(),
                Slack=self._reader.float(),
                Capacity=self._reader.float(),
                Stability=self._reader.float(),
                GoldenMove=bool(self._reader.uint32()),
                EnergyEvaluation=bool(self._reader.uint32()),
                TimingEvaluation=bool(self._reader.uint32()),
                CustomFloats=self._reader.vector(),
                CustomInts=self._reader.array(
                    self._reader.uint32
                ),  # TODO: Check int size
                ScoreOffset=self._reader.float(),
                ScoreScale=self._reader.float(),
                ScoreSmooth=self._reader.float(),
                ScoringMode=self._reader.uint32(),
            )
        elif bank == Banks.EVENT:
            return self._deserialize_event(name, creation_id)
        else:
            logger.warning(f"UNKNOWN DATABANK {bank=}")

    def _deserialize_event(self, name: str, creation_id: int) -> Event:
        current_struct = self._reader.get_struct()
        struct_end = current_struct.seed + current_struct.size_of

        event = Event(
            name=name,
            CreationId=creation_id,
            DefaultDuration=self._reader.uint32(),
            SubdivisionsInBeat=self._reader.uint32(),
        )

        try:
            while self._reader.tell() < struct_end:
                param_name = self._reader.string8()
                if param_name == "Class" or any(
                    param for param in event.Params if param.name == "Class"
                ):
                    class_id = self._reader.int32()

                # TODO: add handler with known param names
                event.Params.append(
                    BankParam(
                        name=param_name,
                        type=PARAM_TO_TYPE.get(param_name, ParamType.INT),
                        DisplayInTimeline=1,
                        DefaultValue="",
                    )
                )
        finally:
            self._reader.seek(struct_end)  # Always seek to struct end, even on error

        return event

    @lyn_struct
    def _deserialize_layers(self, databank: DataBank) -> list[Layer]:
        return list(
            filter(
                None,
                (
                    self._deserialize_layer(position, databank)
                    for position in range(self._reader.uint32())
                ),
            )
        )

    @lyn_struct
    def _deserialize_layer(
        self, position: int, databank: DataBank
    ) -> PictoLayer | MoveLayer | EventsLayer | LyricsLayer | None:
        bank = Banks(self._reader.uint32())
        logger.debug(f"Deserializing LAYER ({bank.name}={bank})")
        if bank == Banks.PICTO:
            return self._deserialize_picto_layer(position, databank)
        if bank in (Banks.MOVE, Banks.KINECTMOVE):
            return self._deserialize_move_layer(position, databank)
        if bank == Banks.EVENT:
            return self._deserialize_event_layer(position, databank)
        if bank == Banks.LYRICS:
            return self._deserialize_lyrics_layer(position)
        logger.error(f"UNKNOWN BANK {bank=}. SKIPPING...")

    def _deserialize_picto_layer(self, position: int, databank: DataBank) -> PictoLayer:
        entries = self._reader.uint32()
        return PictoLayer(
            position=position,
            name=self._reader.string8(),
            instances=[
                self._deserialize_picto_instance(databank) for _ in range(entries)
            ],
        )

    @lyn_struct
    def _deserialize_picto_instance(self, databank: DataBank) -> Instance:
        logger.debug(f"Deserializing PICTO INSTANCE {self._reader.tell()}")
        bank = self._reader.uint32()
        if bank != Banks.PICTO:
            logger.warning(f"Foreign instance in PICTO layer. ({bank})")
        date = self._reader.float()  # Not serialized in Binary
        name_id = self._reader.uint32()
        name = next(
            (entry.name for entry in databank.PictoBank if entry.CreationId == name_id),
            "",
        )
        if not name:
            logger.warning(f"Picto instance {name_id=} is not in PictoBank.")
        position, _offset = self.get_virtual_position(date)
        # Not serialized in XML (calculated through the position)
        return Instance(
            position=position,
            model=name,
            date=date,
        )

    def _deserialize_move_layer(
        self, position: int, databank: DataBank
    ) -> MoveLayer | EventsLayer:
        entries = self._reader.uint32()
        name = self._reader.string8()

        # Storyboard shares BankId with Gestures
        if name == "Storyboard":
            return EventsLayer(
                position=position,
                name=name,
            )
        # TODO: Add Storyboard parser
        # TODO: Check LyN code to find StoryboardLayer/Bank
        layer = MoveLayer(
            position=position,
            name=name,
        )
        for _ in range(entries):
            layer.instances.append(self._deserialize_move_instance(databank))
            if self.legacy:  # Check? maybe struct size of is rounded up
                self._reader.uint32()
                self._reader.uint32()
                # out of the sizeof struct but the next struct is shifted?
        return layer

    @lyn_struct
    def _deserialize_move_instance(self, databank: DataBank) -> MoveInstance:
        logger.debug(f"Deserializing MOVE INSTANCE {self._reader.tell()}")
        bank = self._reader.uint32()
        if bank not in (Banks.MOVE, Banks.KINECTMOVE):
            logger.warning(f"Foreign instance in MOVE layer. ({bank})")
        date = self._reader.float()
        name_id = self._reader.uint32()
        name = next(
            (
                entry.name
                for entry in chain(databank.MoveBank, databank.KinectMoveBank)
                if entry.CreationId == name_id
            ),
            "",
        )
        if not name:
            logger.warning(
                f"Move instance {name_id=} is not in MoveBank or KinectMoveBank."
            )
        duration = self._reader.float()
        gold_move = bool(self._reader.uint32())

        position, _offset = self.get_virtual_position(date)
        offset_in_subdivisions = (
            self.get_virtual_position(date + duration)[0] - position
        )
        return MoveInstance(
            position=position,
            model=name,
            date=date,
            duration=duration,
            OffsetInSubdivisions=offset_in_subdivisions,
            GoldMove=gold_move,
        )

    def _deserialize_event_layer(
        self, position: int, databank: DataBank
    ) -> EventsLayer:
        entries = self._reader.uint32()
        return EventsLayer(
            position=position,
            name=self._reader.string8(),
            instances=[
                self._deserialize_event_instance(databank) for _ in range(entries)
            ],
        )

    @lyn_struct
    def _deserialize_event_instance(self, databank: DataBank) -> EventInstance:
        logger.debug(f"Deserializing EVENT INSTANCE {self._reader.tell()}.")
        bank_id = self._reader.uint32()
        if bank_id != Banks.EVENT:
            logger.warning(f"Foreign instance in EVENT layer. ({bank_id})")
        date = self._reader.float()
        name_id = self._reader.uint32()
        bank = next(
            (entry for entry in databank.EventsBank if entry.CreationId == name_id),
            None,
        )
        if not bank:
            logger.warning(f"Event instance {name_id=} is not in EventBank.")
        else:
            logger.debug(
                f"Deserializing event instance of bank {bank.name} ({bank.CreationId})"
            )
        length = self._reader.float()
        params = self._reader.uint32()
        if not bank:
            logger.warning(f"Bank ({bank_id=}) was not found.")
        elif params != len(bank.Params):
            logger.warning(
                f"Mismatch of bank params {len(bank.Params)} with instance params {params}."
            )
        position, offset = self.get_virtual_position(date)
        event = EventInstance(
            position=position,
            model=bank.name,
            date=date,
            Offset=offset,
            Length=length,
            color="0x00000000",
        )
        if params == 0:
            return event
        params_bank = self._reader.uint32()
        if params_bank != Banks.EVENT:
            logger.warning(f"Foreign param instances in EVENT layer. ({params_bank})")

        for idx, param in enumerate(bank.Params):
            if param.type == ParamType.STRING:
                value = self._reader.string8()
            elif param.type == ParamType.FLOAT:
                value = self._reader.float()
            elif param.type == ParamType.VECTOR:
                value = self._reader.vector()
            else:  # Fallback Int
                value = self._reader.int32()
            # Some instances have alignment?
            event.Params.append(InstanceParam(name=param.name, value=value))
        return event

    def _deserialize_lyrics_layer(self, position: int) -> LyricsLayer:
        entries = self._reader.uint32()
        return LyricsLayer(
            position=position,
            name=self._reader.string8(),
            instances=[self._deserialize_lyrics_instance() for _ in range(entries)],
        )

    @lyn_struct
    def _deserialize_lyrics_instance(self) -> LyricsInstance:
        logger.debug(f"Deserializing LYRICS INSTANCE ({self._reader.tell()})")
        bank = self._reader.uint32()
        if bank != Banks.LYRICS:
            logger.warning(f"Foreign instance in LYRICS layer. ({bank})")
        date = self._reader.float()
        length = self._reader.float()
        text = self._reader.string16().encode("utf-8").decode("utf-8")
        # recode from UTF-16 to UTF-8
        position, offset = self.get_virtual_position(date)
        return LyricsInstance(
            position=position,
            model="Lyrics",
            date=date,
            Offset=offset,
            Length=length,
            Text=text,
        )
