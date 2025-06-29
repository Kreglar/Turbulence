# gui
from PyQt6 import QtWidgets as qtw

# custom utilities
from utils import data
from utils import files
from utils import project

# custom gui widgets
from gui import mainAppWidgets
from gui import paletteEditor
from gui import tilesetEditor
from gui import chunksetEditor
from gui import tilemapEditor

class Application(qtw.QMainWindow):
    """ Main application class. """
    def __init__(self):
        super().__init__()

        # create a blank new project
        self.filename = "untitled.tge"
        self.projectData = project.NewProjectFile()

        # create main enviroment
        self.ResetMainGui()

    def ResetMainGui(self):
        """ Creates/recreates the main enviroment. """
        # set window properties
        self.setWindowTitle("Turbulence - " + self.filename)
        self.setGeometry(100, 100, 1400, 900)

        # set menubar
        self.menu = mainAppWidgets.MenuBar(self)
        self.setMenuBar(self.menu)

        # windows for differnet editors
        self.editors = qtw.QTabWidget(self)
        # - palette editor
        self.palEdit = paletteEditor.PaletteEditor(self)
        self.editors.addTab(self.palEdit, "Palettes")
        # - tileset editor
        self.tileEdit = tilesetEditor.TilesetEditor(self)
        self.editors.addTab(self.tileEdit, "Tileset")
        # - chunkset editor
        self.chunkEdit = chunksetEditor.ChunksetEditor(self)
        self.editors.addTab(self.chunkEdit, "Chunkset")
        # - tilemap editor
        self.mapEdit = tilemapEditor.TilemapEditor(self)
        self.editors.addTab(self.mapEdit, "Tilemap")
        # set the central widget
        self.setCentralWidget(self.editors)

        # link signals
        # - change in palette
        for pv in self.palEdit.palettePanel.visuals:
            # -- tileset editor
            pv.paletteChange.connect(self.tileEdit.colorPanel.picker.ResetImage)
            pv.paletteChange.connect(self.tileEdit.tilesetPanel.ResetImage)
            # -- chunkset editor
            pv.paletteChange.connect(self.chunkEdit.tilePanel.picker.ResetImage)
            pv.paletteChange.connect(self.chunkEdit.tilePanel.palPicker.ResetImage)
            pv.paletteChange.connect(self.chunkEdit.chunksetPanel.ResetImage)
            # -- tilemap editor
            pv.paletteChange.connect(self.mapEdit.chunkPanel.picker.ResetImage)
            pv.paletteChange.connect(self.mapEdit.tilemapPanel.ResetImage)
        # - change in tile
        # -- chunkset editor
        self.tileEdit.tilesetPanel.tileChange.connect(self.chunkEdit.tilePanel.picker.ResetImage)
        self.tileEdit.tilesetPanel.tileChange.connect(self.chunkEdit.chunksetPanel.ResetImage)
        # -- tilemap editor
        self.tileEdit.tilesetPanel.tileChange.connect(self.mapEdit.chunkPanel.picker.ResetImage)
        self.tileEdit.tilesetPanel.tileChange.connect(self.mapEdit.tilemapPanel.ResetImage)
        # - change in chunk
        self.chunkEdit.chunksetPanel.chunkChange.connect(self.mapEdit.chunkPanel.picker.ResetImage)
        self.chunkEdit.chunksetPanel.chunkChange.connect(self.mapEdit.tilemapPanel.ResetImage)

        # reset everything
        for i in range(4):
            self.palEdit.palettePanel.visuals[i].ResetImage()
        self.tileEdit.colorPanel.picker.ResetImage()
        self.tileEdit.tilesetPanel.ResetImage()
        self.chunkEdit.tilePanel.picker.ResetImage()
        self.chunkEdit.tilePanel.palPicker.ResetImage()
        self.chunkEdit.chunksetPanel.ResetImage()
        self.mapEdit.chunkPanel.picker.ResetImage()
        self.mapEdit.tilemapPanel.ResetImage()
    
    def SaveNewProjectFile(self):
        """ Save the project as a new file. """
        # create file dialog
        dialog = qtw.QFileDialog(self)
        dialog.setFileMode(qtw.QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Project Files (*.tge)") # tge = Turbulence Graphics Editor
        dialog.setViewMode(qtw.QFileDialog.ViewMode.Detail)

        # if a file is not chosen
        if not (dialog.exec() and dialog.selectedFiles()):
            return
        
        self.filename = dialog.selectedFiles()[0] # we only want the first file

    def SaveProjectFile(self):
        """ Save the project as a file. """
        # if the file doesn't exsist
        if self.filename == "untitled.tge":
            self.SaveNewProjectFile()
            return

        # convert the project data to json
        jsonData = {"palettes": [[(col.red, col.green, col.blue) for col in pal.palette] for pal in self.projectData.palettes], "tileset": {"size": self.projectData.tileset.size, "set": self.projectData.tileset.set}, "chunkset": {"size": self.projectData.chunkset.size,"chunkSize": self.projectData.chunkset.chunkSize, "set": [[[(tile.palette, tile.id, tile.priority, tile.hFlip, tile.vFlip) for tile in row] for row in chunk] for chunk in self.projectData.chunkset.set]}, "tilemap": {"size": self.projectData.tilemap.size, "map": [[(chunk.id, chunk.hFlip, chunk.vFlip) for chunk in row] for row in self.projectData.tilemap.map]}}

        # write the json
        files.WriteJson(jsonData, self.filename)
    
    def LoadProjectFile(self):
        """ Load a file into the project. """
        # create file dialog
        dialog = qtw.QFileDialog(self)
        dialog.setFileMode(qtw.QFileDialog.FileMode.ExistingFiles)
        dialog.setNameFilter("Project Files (*.tge)") # tge = Turbulence Graphics Editor
        dialog.setViewMode(qtw.QFileDialog.ViewMode.Detail)

        # if a file is not chosen
        if not (dialog.exec() and dialog.selectedFiles()):
            return
        
        self.filename = dialog.selectedFiles()[0] # we only want the first file
        
        # read the file as json
        jsonData = files.ReadJson(self.filename)

        # redefine all
        self.RedefinePalettes(jsonData)
        self.RedefineTileset(jsonData)
        self.RedefineChunkset(jsonData)
        self.RedefineTilemap(jsonData)

        # reset the gui
        self.ResetMainGui()

    def RedefinePalettes(self, palettesJson: dict):
        """ Set the palettes to the json data. """
        self.projectData.palettes = [data.Palette([data.Color(col[0], col[1], col[2]) for col in palettesJson["palettes"][palIndex]]) for palIndex in range(4)]
    
    def RedefineTileset(self, tilesetJson: dict):
        """ Set the tileset to the json data. """
        self.projectData.tileset = data.Tileset(tilesetJson["tileset"]["size"], tilesetJson["tileset"]["set"])
    
    def RedefineChunkset(self, chunksetJson: dict):
        """ Set the chunkset to the json data. """
        self.projectData.chunkset = data.Chunkset(chunksetJson["chunkset"]["size"], chunksetJson["chunkset"]["chunkSize"], [[[data.Tile(chunksetJson["chunkset"]["set"][i][y][x][0], chunksetJson["chunkset"]["set"][i][y][x][1], chunksetJson["chunkset"]["set"][i][y][x][2], chunksetJson["chunkset"]["set"][i][y][x][3], chunksetJson["chunkset"]["set"][i][y][x][4]) for x in range(chunksetJson["chunkset"]["chunkSize"])] for y in range(chunksetJson["chunkset"]["chunkSize"])] for i in range(chunksetJson["chunkset"]["size"])])
    
    def RedefineTilemap(self, tilemapJson: dict):
        """ Set the tilemap to the json data. """
        self.projectData.tilemap = data.Tilemap(tilemapJson["tilemap"]["size"], [[data.Chunk(tilemapJson["tilemap"]["map"][y][x][0], tilemapJson["tilemap"]["map"][y][x][1], tilemapJson["tilemap"]["map"][y][x][2]) for x in range(tilemapJson["tilemap"]["size"][0])] for y in range(tilemapJson["tilemap"]["size"][1])])
