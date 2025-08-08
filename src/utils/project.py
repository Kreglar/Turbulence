from dataclasses import dataclass

# gui
from PyQt6 import QtWidgets as qtw

# various data types used in this project
from . import data

@dataclass
class ProjectData:
    # define sets and maps
    palettes: list[data.Palette]
    tileset: data.Tileset
    tilemap: data.Tilemap

def NewProjectFile() -> ProjectData:
    # define defaults
    palettes = [data.Palette() for i in range(4)]
    tileset = data.Tileset(1600) # 1600 unique tiles
    tilemap = data.Tilemap((256, 128)) # 256x128 tile tilemap

    # create project dataclass
    projectFile = ProjectData(palettes, tileset, tilemap)
    return projectFile
