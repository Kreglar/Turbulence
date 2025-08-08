from dataclasses import dataclass

@dataclass
class Color:
    """ Red, green, and blue ints represnting a color. """
    red: int
    green: int
    blue: int

class Palette:
    """ Set of 16 colors. """
    def __init__(self, palette: list[Color] | None=None):
        # define palette (stores rgb color format)
        if not palette:
            self.palette = [Color(0, 0, 0) for i in range(16)]
        else:
            self.palette = palette
    
    def AddColor(self, color: Color, colorIndex: int) -> None:
        """ Add a color to a specific location in the palette. """
        # add the color
        self.palette[colorIndex] = color
    
    def GetColor(self, colorIndex: int) -> Color:
        """ Get a specific color from the palette. """
        # return the color
        return self.palette[colorIndex]

class Tileset:
    """ Set of tiles. """
    def __init__(self, size: int, set: list[list[list[int]]] | None=None):
        # define globals
        self.size = size
        # fill with blank tiles to desired size
        if not set:
            self.set = [[[0 for x in range(8)] for y in range(8)] for t in range(size)]
        else:
            self.set = set

@dataclass
class Tile:
    """ Reference to a tile in the tileset. """
    palette: int
    id: int
    priority: bool=False # false=low, true=high
    hFlip: bool=False
    vFlip: bool=False

class Tilemap:
    """ Map of tiles. """
    def __init__(self, size: tuple[int, int], map: list[list[Tile]] | None=None):
        # define global
        self.size = size

        # fill with blank tiles
        if not map:
            self.map = [[Tile(palette=0, id=0) for x in range(size[0])] for y in range(size[1])]
        else:
            self.map = map
