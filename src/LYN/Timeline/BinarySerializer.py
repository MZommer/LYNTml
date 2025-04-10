import datetime
import functools
import struct
from io import BytesIO
from typing import List, BinaryIO, Union, Tuple, Optional, Callable

from .__types__ import (
    Banks, Move, Gesture, Event,
    PictoLayer, MoveLayer, LyricsLayer, EventLayer,
    Instance, MoveInstance, LyricsInstance, EventInstance, Timeline
)
from ..BinaryReader import BinaryReader
from ..Logger import logger

LEGACY_VERSION = 9


# Decorator
def lyn_struct(_func: Optional[Callable] = None, *, trustable: bool = False):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            info = self._reader.init_struct()
            try:
                ret = func(self, *args, **kwargs)
            except Exception as e:
                self._reader.seek(info.seed)  # rollback
                logger.error(f"Error in {func.__name__}: {e}")
                ret = None
            finally:
                current = self._reader.tell()
                end_expected = info.seed + info.size_of
                if current < end_expected:
                    logger.debug(f"[{func.__name__}] Struct ended early: {current} < {end_expected}")
                if current > end_expected + (8 if trustable else 0):
                    logger.debug(f"[{func.__name__}] Struct overread: {current} > {end_expected}")
                self._reader.seek(end_expected)
            return ret

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


class BinarySerializer:
    _reader: BinaryReader

    timeline: Timeline

    # local state #
    virtualstart: List[float]

    def __init__(self) -> None:
        self.timeline = Timeline()

        self.names = []
        self.virtualstart = []

    def deserialize(self, stream: Union[BinaryIO, bytes]) -> Timeline:
        if isinstance(stream, bytes):
            stream = BytesIO(stream)
        self._reader = BinaryReader("LITTLE", stream)
        self._deserialize_timeline()
        return self.timeline

    # Helper functions #    
    def get_virtual_position(self, time: Union[int, float]) -> Tuple[int, float]:
        if not self.virtualstart:
            return 0, time
        position = self.virtualstart.index(min(self.virtualstart, key=lambda item: abs(item - time)))
        offset = time - self.virtualstart[position]
        return position, offset

    # Reader functions #
    @lyn_struct
    def _deserialize_timeline(self):
        self._deserialize_general()
        self._deserialize_virtual_start()
        self._deserialize_data_bank()
        self._deserialize_layers()

    @lyn_struct
    def _deserialize_general(self) -> None:
        version = self._reader.float()

        song = self._reader.string()
        beats_per_measure = self._reader.uint32()
        first_measure_marker_pos = self._reader.uint32()
        beats_per_minute = self._reader.uint32()
        sample_frequency = self._reader.uint32()
        wave_nb_samples = self._reader.uint32() if version > LEGACY_VERSION else 0
        custom_score_steps = bool(self._reader.uint32())

        for _ in range(self._reader.uint32()):
            name = self._reader.string()
            value = self._reader.uint32()
            self.timeline.general.ScoreSteps.add_score_step(name, value)

        self.timeline.version = version

        self.timeline.general.Song = song
        self.timeline.general.BeatsPerMinute = beats_per_minute
        self.timeline.general.SampleFrequency = sample_frequency
        self.timeline.general.BeatsPerMeasure = beats_per_measure
        self.timeline.general.FirstMeasureMarkerPos = first_measure_marker_pos
        self.timeline.general.WaveNbSamples = wave_nb_samples
        self.timeline.general.CustomScoreSteps = custom_score_steps

        # Not serialized values #
        now = datetime.datetime.now()
        date = now.strftime("%d/%m/%Y %H:%M:%S")

        self.timeline.general.LastMoveChangeDate = date
        self.timeline.general.LastClassifierChangeDate = date
        self.timeline.general.LastPictoModelCreateDeleteDate = date

        self.timeline.general.WavePath = rf".\Sounds\{song}.wav"
        self.timeline.general.VideoPath = rf".\{song}\Videos\{song}.bik"
        self.timeline.general.PictoFolder = r".\Pictos"

    @lyn_struct
    def _deserialize_virtual_start(self) -> None:
        self._reader.uint32()  # 0x00

        for position in range(self._reader.uint32()):
            sampleposition = self._reader.float()
            date = self._reader.float()
            name = self._reader.string()

            self.timeline.markerlist.add_marker(position, name, sampleposition, date)

            self.virtualstart.append(date)

    @lyn_struct
    def _deserialize_data_bank(self) -> None:
        print("version", self.timeline.version)
        for _ in range(self._reader.uint32()):
            self._deserialize_bank()

    @lyn_struct(trustable=True)
    def _deserialize_bank(self) -> None:
        bank = self._reader.uint32()
        name = self._reader.string()

        if bank == Banks.LYRICS:
            logger.debug("LYRICS BANK?")

        elif bank == Banks.PICTO:
            picto = self.timeline.databank.add_picto(name, len(self.timeline.databank.PictoBank))

        elif bank == Banks.MOVE:
            move = self._deserialize_move(name)

        elif bank == Banks.EVENTS:
            event = self._deserialize_event(name)

        elif bank == Banks.GESTURES:
            gesture = self._deserialize_gesture(name)

        else:
            logger.warning(f"UNKNOWN DATABANK {bank=}")

    def _deserialize_move(self, name: str) -> Move:
        creation_id = len(self.timeline.databank.MoveBank)
        duration = 2
        subdivisions_in_beat = 2
        color = "0x00000000"  # Not serialized data?
        livemove_mul = self._reader.float()
        livemove_plus = self._reader.float()
        slack = self._reader.float()
        capacity = self._reader.float()
        stability = self._reader.float()
        golden_move = bool(self._reader.uint32())
        energy_evaluation = bool(self._reader.uint32())
        timing_evaluation = bool(self._reader.uint32())
        custom_floats = self._reader.vector()
        self._reader.uint32()  # terminator?

        move = self.timeline.databank.add_move(
            name, creation_id, duration, subdivisions_in_beat, color, livemove_mul,
            livemove_plus, slack, capacity, stability, golden_move, energy_evaluation,
            timing_evaluation, custom_floats
        )
        return move

    def _deserialize_gesture(self, name: str) -> Gesture:
        creation_id = len(self.timeline.databank.GestureBank)
        duration = 2
        subdivisions_in_beat = 2
        color = "0x00000000"
        gesture_mul = self._reader.float()
        gesture_plus = self._reader.float()
        slack = self._reader.float()
        capacity = self._reader.float()
        stability = self._reader.float()
        golden_move = bool(self._reader.uint32())
        energy_evaluation = bool(self._reader.uint32())
        timing_evaluation = bool(self._reader.uint32())
        custom_floats = self._reader.vector()
        self._reader.uint32()  # terminator?
        gesture = self.timeline.databank.add_gesture(
            name, creation_id, duration, subdivisions_in_beat, color,
            gesture_mul, gesture_plus, slack, capacity, stability, golden_move,
            energy_evaluation, timing_evaluation, custom_floats
        )
        # TODO: add gesture struct
        return gesture

    def _deserialize_event(self, name: str) -> Optional[Event]:
        info = self._reader.get_struct()
        struct_end = info.seed + info.size_of

        creation_id = len(self.timeline.databank.EventsBank)
        default_duration = self._reader.uint32()
        subdivisions_in_beat = self._reader.uint32()
        event = self.timeline.databank.add_event(
            name, creation_id, subdivisions_in_beat, default_duration
        )

        # Legacy format handling
        is_legacy = self.timeline.version <= LEGACY_VERSION
        try:
            while self._reader.tell() < struct_end:
                param_name = self._reader.string()
                if param_name == "Class":
                    is_legacy = True
                if is_legacy:
                    _ = self._reader.int32()  # legacy extra value, skipped

                # TODO: add handler with known param names
                param_type = None
                display_in_timeline = 1
                default_value = ""
                event.add_param(param_name, param_type, display_in_timeline, default_value)
        finally:
            self._reader.seek(info.seed + info.size_of)  # Always seek to struct end, even on error

        return event

    @lyn_struct
    def _deserialize_layers(self) -> None:
        for position in range(self._reader.uint32()):
            self._deserialize_layer(position)

    @lyn_struct
    def _deserialize_layer(self, position: int) -> None:
        bank = self._reader.uint32()
        if bank == Banks.PICTO:
            layer = self._deserialize_picto_layer(position)
        elif bank == Banks.MOVE or bank == Banks.GESTURES:
            layer = self._deserialize_move_layer(position)
        elif bank == Banks.EVENTS:
            layer = self._deserialize_event_layer(position)
        elif bank == Banks.LYRICS:
            layer = self._deserialize_lyrics_layer(position)
        else:
            layer = None
            logger.error(f"UNKNOWN BANK {bank=}")
        if layer:
            self.timeline.append(layer)

    def _deserialize_picto_layer(self, position: int) -> PictoLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = PictoLayer(name, Banks.id2name(Banks.PICTO), position)
        for _ in range(entries):
            instance = self._deserialize_picto_instance()
            if instance:
                layer.append(instance)
        return layer

    @lyn_struct
    def _deserialize_picto_instance(self) -> Instance:
        bank = self._reader.uint32()
        # TODO: add bank checker?
        date = self._reader.float()
        name_id = self._reader.uint32()
        position, offset = self.get_virtual_position(date)
        return Instance(position, self.timeline.databank.get_bank(name_id), date)

    def _deserialize_move_layer(self, position: int) -> Union[MoveLayer, EventLayer]:
        entries = self._reader.uint32()
        name = self._reader.string()

        if name == "Storyboard":
            return EventLayer(name, Banks.id2name(Banks.EVENTS), position)
        # Storyboard shares BankId with Gestures
        # TODO: Add Storyboard parser
        # TODO: Check LyN code to find StoryboardLayer/Bank
        layer = MoveLayer(name, Banks.id2name(Banks.MOVE), position)
        for _ in range(entries):
            instance = self._deserialize_move_instance()
            if instance:
                layer.append(instance)
            if self.timeline.version > LEGACY_VERSION:
                self._reader.uint32()
                self._reader.uint32()
                # out of the sizeof struct but the next struct is shifted?
        return layer

    @lyn_struct
    def _deserialize_move_instance(self) -> MoveInstance:
        bank = self._reader.uint32()
        date = self._reader.float()
        name_id = self._reader.uint32()
        duration = self._reader.float()
        gold_move = bool(self._reader.uint32())

        position, offset = self.get_virtual_position(date)
        offset_in_subdivisions = self.get_virtual_position(date + duration)[0] - position
        return MoveInstance(
            position,
            self.timeline.databank.get_bank(name_id),
            date,
            duration,
            gold_move,
            offset_in_subdivisions,
        )

    def _deserialize_event_layer(self, position: int) -> EventLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = EventLayer(name, Banks.id2name(Banks.EVENTS), position)
        for _ in range(entries):
            instance = self._deserialize_event_instance()
            if instance:
                layer.append(instance)
        return layer

    @lyn_struct
    def _deserialize_event_instance(self) -> EventInstance:
        bank = self._reader.uint32()
        date = self._reader.float()
        name_id = self._reader.uint32()
        name = self.timeline.databank.get_bank(name_id)
        length = self._reader.float()
        color = "0x00000000"
        default_duration = self._reader.uint32()
        if self.timeline.version > LEGACY_VERSION:
            subdivisions_in_beat = self._reader.uint32()
        position, offset = self.get_virtual_position(date)
        event = EventInstance(position, name, offset, length, color)
        for bank in self.timeline.databank.find_bank(name):
            if bank.tag != "Event":
                continue
            for idx, param in enumerate(bank.Params):
                if param.type == "String":
                    value = self._reader.string()
                    if param.name == "Class":
                        self._reader.uint32()
                        self._reader.uint32()
                        # ???
                elif param.type == "Float":
                    value = self._reader.float()
                else:
                    value = self._reader.int32()
                if idx == 0 and param.name != "Class":
                    try:
                        self._reader.uint32()
                        self._reader.uint32()
                    except struct.error:
                        pass  # IDK the last instance doesn't have this
                    # ???
                event.AddParam(param.name, value)
        return event

    def _deserialize_lyrics_layer(self, position: int) -> LyricsLayer:
        entries = self._reader.uint32()
        name = self._reader.string()
        layer = LyricsLayer(name, Banks.id2name(Banks.LYRICS), position)
        for _ in range(entries):
            instance = self._deserialize_lyrics_instance()
            if instance:
                layer.append(instance)
        return layer

    @lyn_struct(trustable=True)
    def _deserialize_lyrics_instance(self) -> LyricsInstance:
        bank = self._reader.uint32()
        date = self._reader.float()
        length = self._reader.float()
        text = self._reader.string(True).encode("utf-8").decode("utf-8")

        position, offset = self.get_virtual_position(date)
        return LyricsInstance(position, "Lyrics", date, length, text)
