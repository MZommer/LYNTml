from typing import Tuple, Dict, List, Union, Optional

from .Timeline.__types__ import Timeline, Instance, MoveInstance, LyricsInstance


def index_resolver(name: str) -> int:
    if name[-1].isdigit():
        idx = int(name[-1]) - 1
        if idx < 0:
            return 0
        return idx
    return 0


class BlueStarConverter:
    main: Dict[str, Optional[Union[str, int]]]
    moves: Tuple[List[Dict[str, Union[str, int]]], ...] = [], [], [], []
    kinectmoves: Tuple[List[Dict[str, Union[str, int]]], ...] = [], [], [], []
    
    def __init__(self, timeline: Timeline):
        self.timeline = timeline
        self.to_blue_star()
        
    def picto_instance_resolver(self, instance: Instance) -> Dict[str, Union[str, int]]:
        position_date = self.timeline.markerlist[instance.position].date
        date = instance.date or position_date
        duration = self.timeline.markerlist[instance.position + 1].date - date
        return {
            "name": instance.model,
            "time": int(date * 1000),
            "duration": int(duration * 1000),
        }
    
    def move_instance_resolver(self, instance: MoveInstance) -> Dict[str, Union[str, int]]:
        position_date = self.timeline.markerlist[instance.position].date
        date = instance.date or position_date
        duration = instance.duration or self.timeline.markerlist[instance.position + instance.OffsetInSubdivisions].date - date
        return {
            "name": instance.model,
            "time": int(date * 1000),
            "duration": int(duration * 1000),
            "goldMove": int(instance.GoldMove),
        }
    
    def lyrics_instance_resolver(self, instance: LyricsInstance) -> Dict[str, Union[str, int]]:
        position_date = self.timeline.markerlist[instance.position].date
        date = position_date + instance.Offset
        duration = instance.Length
        text = instance.Text.replace("_", " ")
        
        return {
            "time": int(date * 1000),
            "duration": int(duration * 1000),
            "text": text,
            "isLineEnding": 1,
        }
        
        
    def to_blue_star(self) -> None:
        beats = sorted(marker.date * 1000 for marker in self.timeline.markerlist)
        pictos = []
        lyrics = []
        karaoke = []
        
        for layer in self.timeline.iter("Layer"):
            if layer.type == "Move":
                idx = index_resolver(layer.name)
                
                for instance in layer:
                    clip = self.move_instance_resolver(instance)
                    
                    if layer.name.startswith("Kinect"):
                        self.kinectmoves[idx].append(clip)
                    else:
                        self.moves[idx].append(clip)
            
            elif layer.type == "Picto":
                for instance in layer:
                    clip = self.picto_instance_resolver(instance)
                    pictos.append(clip)

            elif layer.type == "Lyrics":
                for instance in layer:
                    clip = self.lyrics_instance_resolver(instance)
                    if layer.name.lower().startswith("karaoke"):
                        karaoke.append(clip)
                    else:
                        lyrics.append(clip)
            
            elif layer.type == "Events":
                for instance in layer:
                    pass
                    
                    
            
        self.main = {
            "MapName": self.timeline.general.Song,
            "Artist": "Unknown",
            "Title": self.timeline.general.Song,
            "NumCoach": len(tuple(move for move in self.moves if move)),
            "beats": beats,
            "goldEffects": [],
            "lyrics": karaoke or lyrics or [],
            "pictos": pictos
        }
        
        