# gui
from PyQt6 import QtWidgets as qtw

# custom utilities
from utils import data
from utils import files
from utils import project

# custom gui widgets
from gui import common
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
        self.projectData = project.NewProjectFile()

        # set window properties
        self.setWindowTitle("Turbulence - FILE.EXT")
        self.setGeometry(100, 100, 1400, 900)

        # set menubar
        menu = mainAppWidgets.MenuBar(self)
        self.setMenuBar(menu)

        # set toolbar
        toolbar = mainAppWidgets.Toolbar(self)
        self.addToolBar(toolbar)

        # windows for differnet editors
        editors = qtw.QTabWidget(self)
        # - palette editor
        palEdit = paletteEditor.PaletteEditor(self)
        editors.addTab(palEdit, "Palettes")
        # - tileset editor
        tileEdit = tilesetEditor.TilesetEditor(self)
        editors.addTab(tileEdit, "Tileset")
        # - chunkset editor
        chunkEdit = chunksetEditor.ChunksetEditor(self)
        editors.addTab(chunkEdit, "Chunkset")
        # - tilemap editor
        mapEdit = tilemapEditor.TilemapEditor(self)
        editors.addTab(mapEdit, "Tilemap")
        # set the central widget
        self.setCentralWidget(editors)

        # link signals
        # - change in palette
        for pv in palEdit.palettePanel.visuals:
            # - tileset editor
            pv.paletteChange.connect(tileEdit.colorPanel.picker.ResetImage)
            pv.paletteChange.connect(tileEdit.tilesetPanel.ResetImage)
            # - chunkset editor
            pv.paletteChange.connect(chunkEdit.tilePanel.picker.ResetImage)
            pv.paletteChange.connect(chunkEdit.chunksetPanel.ResetImage)
        # - change in tile
        # -- chunkset editor
        tileEdit.tilesetPanel.tileChange.connect(chunkEdit.tilePanel.picker.ResetImage)
        tileEdit.tilesetPanel.tileChange.connect(chunkEdit.chunksetPanel.ResetImage)
