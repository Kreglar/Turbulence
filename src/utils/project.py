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
    chunkset: data.Chunkset
    tilemap: data.Tilemap

def NewProjectFile() -> ProjectData:
    # define defaults
    palettes = [data.Palette() for i in range(4)]
    tileset = data.Tileset(1600) # 1600 unique tiles
    chunkset = data.Chunkset(400, 4) # 400 unique chunks, 4x4 tiles per chunk
    tilemap = data.Tilemap((64, 32)) # 64x32 chunk tilemap

    # create project dataclass
    projectFile = ProjectData(palettes, tileset, chunkset, tilemap)
    return projectFile

def LoadProjectFile(mainApplication: object, projectFile: dict) -> None: # TODO
    """ Load a project file into the editor. """

def ImportFile():
    pass

def ExportFile():
    pass
