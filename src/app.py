# gui
from PyQt6 import QtWidgets as qtw

# to extract file extensions
import pathlib

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

        # redefine palettes with json data
        self.projectData.palettes = [
            data.Palette(
                [data.Color(col[0], col[1], col[2]) for col in jsonData["palettes"][palIndex]]
            ) for palIndex in range(4)
        ]
        
        # redefine tileset with json data
        self.projectData.tileset = data.Tileset(jsonData["tileset"]["size"], jsonData["tileset"]["set"])
        
        # redefine chunkset with json data
        self.projectData.chunkset = data.Chunkset(
            jsonData["chunkset"]["size"],
            jsonData["chunkset"]["chunkSize"],

            [
                [
                    [
                        data.Tile(
                            tile[0], # palette index
                            tile[1], # tile id
                            tile[2], # tile priority
                            tile[3], # tile horizontal flip
                            tile[4] # tile vertical flip
                        ) for tile in row
                    ] for row in chunk
                ] for chunk in jsonData["chunkset"]["set"]
            ]
        )
        
        # redefine tilemap with json data
        self.projectData.tilemap = data.Tilemap(
            jsonData["tilemap"]["size"],

            [
                [
                    data.Chunk(
                        chunk[0], # chunk id
                        chunk[1], # chunk horizontal flip
                        chunk[2] # chunk vertical flip
                    ) for chunk in row
                ] for row in jsonData["tilemap"]["map"]
            ]
        )

        self.ResetMainGui()
    
    def ImportFile(self, type: str):
        """ Import data into the project. """
        # get type of import
        if type == "Palette":
            # create file dialog
            dialog = qtw.QFileDialog(self)
            dialog.setFileMode(qtw.QFileDialog.FileMode.ExistingFiles)
            dialog.setNameFilter("All Files (*.*);;Image files (*.png, *.bmp, *.jpg);;Assembly Files (*.asm, *.s);;Binary Files (*.bin)")
            dialog.setViewMode(qtw.QFileDialog.ViewMode.Detail)

            # if a file is not chosen
            if not (dialog.exec() and dialog.selectedFiles()):
                return
            
            # get where you want to import palette
            importLocation, okPressed = qtw.QInputDialog.getInt(self, "Get Location", "Which palette would you like to import to?", 0, 0, 3, 1)
            if not okPressed:
                return
            
            file = dialog.selectedFiles()[0] # we only want the first file

            # compare file extension
            ext = pathlib.Path(file).suffix
            if ext == ".png" or ext == ".bmp" or ext == ".jpg":
                self.projectData.palettes[importLocation] = files.ExtractPaletteImg(file)
            elif ext == ".asm" or ext == ".s":
                self.projectData.palettes[importLocation] = files.ExtractPalettesBin(files.ExtractBinDataAsm(file))[0]
            elif ext == ".bin":
                self.projectData.palettes[importLocation] = files.ExtractPalettesBin(file)[0]

            # reset gui
            self.ResetMainGui()

        elif type == "Tileset":
            # create file dialog
            dialog = qtw.QFileDialog(self)
            dialog.setFileMode(qtw.QFileDialog.FileMode.ExistingFiles)
            dialog.setNameFilter("All Files (*.*);;Image files (*.png, *.bmp, *.jpg);;Assembly Files (*.asm, *.s);;Binary Files (*.bin)")
            dialog.setViewMode(qtw.QFileDialog.ViewMode.Detail)

            # if a file is not chosen
            if not (dialog.exec() and dialog.selectedFiles()):
                return
            
            file = dialog.selectedFiles()[0] # we only want the first file

            # compare file extension
            ext = pathlib.Path(file).suffix
            if ext == ".png" or ext == ".bmp" or ext == ".jpg":
                self.projectData.tileset = files.ExtractTilesetImg(file)
            elif ext == ".asm" or ext == ".s":
                self.projectData.tileset = files.ExtractTilesetBin(files.ExtractBinDataAsm(file))
            elif ext == ".bin":
                self.projectData.tileset = files.ExtractTilesetBin(file)

            # reset gui
            self.ResetMainGui()

        elif type == "Chunkset":
            # create file dialog
            dialog = qtw.QFileDialog(self)
            dialog.setFileMode(qtw.QFileDialog.FileMode.ExistingFiles)
            dialog.setNameFilter("All Files (*.*);;Assembly Files (*.asm, *.s);;Binary Files (*.bin)")
            dialog.setViewMode(qtw.QFileDialog.ViewMode.Detail)

            # if a file is not chosen
            if not (dialog.exec() and dialog.selectedFiles()):
                return
            
            file = dialog.selectedFiles()[0] # we only want the first file

            # compare file extension
            ext = pathlib.Path(file).suffix
            if ext == ".asm" or ext == ".s":
                self.projectData.tileset = files.ExtractChunksetBin(files.ExtractBinDataAsm(file))
            elif ext == ".bin":
                self.projectData.tileset = files.ExtractChunksetBin(file)

            # reset gui
            self.ResetMainGui()

        elif type == "Tilemap":
            # create file dialog
            dialog = qtw.QFileDialog(self)
            dialog.setFileMode(qtw.QFileDialog.FileMode.ExistingFiles)
            dialog.setNameFilter("All Files (*.*);;Assembly Files (*.asm, *.s);;Binary Files (*.bin)")
            dialog.setViewMode(qtw.QFileDialog.ViewMode.Detail)

            # if a file is not chosen
            if not (dialog.exec() and dialog.selectedFiles()):
                return
            
            file = dialog.selectedFiles()[0] # we only want the first file

            # compare file extension
            ext = pathlib.Path(file).suffix
            if ext == ".asm" or ext == ".s":
                self.projectData.tileset = files.ExtractTilemapBin(files.ExtractBinDataAsm(file))
            elif ext == ".bin":
                self.projectData.tileset = files.ExtractTilemapBin(file)

            # reset gui
            self.ResetMainGui()

    def ExportFile(self, type: str):
        pass
