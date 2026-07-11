from __future__ import annotations
from dataclasses import dataclass

CANVAS=(336,480)
RGBA=tuple[int,int,int,int]
BG=(8,10,16,255); PANEL=(19,24,34,255); GRID=(39,47,62,255)
WHITE=(244,247,251,255); MUTED=(148,158,178,255); ACCENT=(74,222,188,255); ORANGE=(255,137,80,255)

@dataclass
class Indexed:
    width:int
    height:int
    palette:bytes
    indices:bytes

class Canvas:
    def __init__(self,w:int,h:int,colors:list[RGBA],fill:int=0):
        self.w=w;