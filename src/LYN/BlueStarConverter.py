from .Timeline.__types__ import Timeline, Instance

def IndexResolver(name: str) -> int:
    if name[-1].isdigit():
        idx = int(name[-1]) - 1
        if idx < 0:
            return 0
        return idx
    return 0


class BlueStarConverter:
    main: dict
    moves: tuple = [], [], [], []
    kinectmoves: tuple = [], [], [], []
    
    def __init__(self, timeline: Timeline):
        self.timeline = timeline
        self.ToBlueStar()
        
    def PictoInstanceResolver(self, instance: Instance) -> dict:
        position_date = self.timeline.markerlist[instance.position].date
        date = instance.date or position_date
        duration = self.timeline.markerlist[instance.position + 1].date - date
        return {
            "name": instance.model,
            "time": int(date * 1000),
            "duration": int(duration * 1000),
        }
    
    def MoveInstanceResolver(self, instance: Instance) -> dict:
        position_date = self.timeline.markerlist[instance.position].date
        date = instance.date or position_date
        duration = instance.duration or self.timeline.markerlist[instance.position + instance.OffsetInSubdivisions].date - date
        return {
            "name": instance.model,
            "time": int(date * 1000),
            "duration": int(duration * 1000),
            "goldMove": int(instance.GoldMove),
        }
    
    def LyricsInstanceResolver(self, instance: Instance) -> dict:
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
        
        
    def ToBlueStar(self) -> None:        
        beats = sorted(marker.date * 1000 for marker in self.timeline.markerlist)
        pictos = []
        lyrics = []
        karaoke = []
        
        for layer in self.timeline.iter("Layer"):
            if layer.type == "Move":
                idx = IndexResolver(layer.name)
                
                for instance in layer:
                    clip = self.MoveInstanceResolver(instance)
                    
                    if layer.name.startswith("Kinect"):
                        self.kinectmoves[idx].append(clip)
                    else:
                        self.moves[idx].append(clip)
            
            elif layer.type == "Picto":
                for instance in layer:
                    clip = self.PictoInstanceResolver(instance)
                    pictos.append(clip)

            elif layer.type == "Lyrics":
                for instance in layer:
                    clip = self.LyricsInstanceResolver(instance)
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
        
        