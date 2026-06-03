from .timeline.layer import Instance, LayerType, LyricsInstance, MoveInstance
from .timeline.timeline import JustDanceToolLD


def _index_resolver(name: str) -> int:
    if name[-1].isdigit():
        idx = int(name[-1]) - 1
        if idx < 0:
            return 0
        return idx
    return 0


class BlueStarConverter:
    # TODO: Make typeddict
    main: dict[str, str | int | None]
    moves: tuple[list[dict[str, str | int]], ...] = [], [], [], []
    kinectmoves: tuple[list[dict[str, str | int]], ...] = [], [], [], []

    def __init__(self, timeline: JustDanceToolLD) -> None:
        self.timeline = timeline
        self.to_bluestar()

    def picto_instance_resolver(self, instance: Instance) -> dict[str, str | int]:
        position_date = self.timeline.partition.markerlist[instance.position].date
        date = instance.date or position_date
        duration = self.timeline.partition.markerlist[instance.position + 1].date - date
        return {
            "name": instance.model,
            "time": int(date * 1000),
            "duration": int(duration * 1000),
        }

    def move_instance_resolver(self, instance: MoveInstance) -> dict[str, str | int]:
        position_date = self.timeline.partition.markerlist[instance.position].date
        date = instance.date or position_date
        duration = (
            instance.duration
            or self.timeline.partition.markerlist[
                instance.position + instance.OffsetInSubdivisions
            ].date
            - date
        )
        return {
            "name": instance.model,
            "time": int(date * 1000),
            "duration": int(duration * 1000),
            "goldMove": int(instance.GoldMove),
        }

    def lyrics_instance_resolver(
        self, instance: LyricsInstance
    ) -> dict[str, str | int]:
        position_date = self.timeline.partition.markerlist[instance.position].date
        date = position_date + instance.Offset
        duration = instance.Length
        text = instance.Text.replace("_", " ")

        return {
            "time": int(date * 1000),
            "duration": int(duration * 1000),
            "text": text,
            "isLineEnding": 1,
        }

    def to_bluestar(self) -> None:
        beats = sorted(
            marker.date * 1000 for marker in self.timeline.partition.markerlist
        )
        pictos = []
        lyrics = []
        karaoke = []

        for layer in self.timeline.partition.layers:
            if layer.type == LayerType.MOVE:
                idx = _index_resolver(layer.name)

                for instance in layer.instances:
                    clip = self.move_instance_resolver(instance)

                    if layer.name.lower().startswith("kinect"):
                        self.kinectmoves[idx].append(clip)
                    else:
                        self.moves[idx].append(clip)

            elif layer.type == LayerType.PICTO:
                for instance in layer.instances:
                    clip = self.picto_instance_resolver(instance)
                    pictos.append(clip)

            elif layer.type == LayerType.LYRICS:
                for instance in layer.instances:
                    clip = self.lyrics_instance_resolver(instance)
                    if layer.name.lower().startswith("karaoke"):
                        karaoke.append(clip)
                    else:
                        lyrics.append(clip)

            elif layer.type == LayerType.EVENTS:
                for _instance in layer.instances:
                    pass

        self.main = {
            "MapName": self.timeline.partition.general.Song,
            "Artist": "Unknown",
            "Title": self.timeline.partition.general.Song,
            "NumCoach": len(tuple(move for move in self.moves if move)),
            "beats": beats,
            "goldEffects": [],
            "lyrics": karaoke or lyrics or [],
            "pictos": pictos,
        }
