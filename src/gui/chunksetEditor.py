# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

# for common gui items
from . import common

# for direct image manipulation
import numpy

class TilePicker(qtw.QGraphicsView):
    """ Tilepicker used to select tile. """
    # signal to share tile
    tileSelected = qtc.pyqtSignal(int)

    def __init__(self, scale: int, mainApplication: object):
        super().__init__()

        # define globals
        self.imgScale = scale
        self.mainApplication = mainApplication
        self.tileset = mainApplication.projectData.tileset
        self.currentPaletteIndex = 0
        self.currentHFlip = False
        self.currentVFlip = False

        # scene/image init
        self.graphicsScene = qtw.QGraphicsScene()
        self.setScene(self.graphicsScene)

        # define the tile choice img
        self.img = qtg.QPixmap(8, self.tileset.size * 8)
        self.img.fill(qtg.QColor(0, 0, 0)) # fill with black

        # create the label holding the img
        self.pixmapItem = self.graphicsScene.addPixmap(self.img)

        # create selection overlay
        self.overlay = qtg.QPixmap(scale, self.tileset.size * scale)
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent

        # fix the size
        self.setFixedSize(scale + 16, scale * 16) # +16 makes room for the scroll bar

        # always have vertical scroll bar
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # create image once to edit later
        width = self.img.width()
        height = self.img.height()
        self.image = qtg.QImage(width, height, qtg.QImage.Format.Format_ARGB32)

        # set the scale
        self.resetTransform()
        self.scale(self.imgScale // 8, self.imgScale // 8)
    
    def SetProperties(self, priority: bool, palette: int, hFlip: bool, vFlip: bool):
        """ Set the properties of what is selected. """
        self.currentPaletteIndex = palette
        self.currentHFlip = hFlip
        self.currentVFlip = vFlip

        # redraw the image
        self.ResetImage()

    def ResetImage(self):
        """ Redraw the image. """
        # create blank image
        width = self.img.width()
        height = self.img.height()

        # grab palette/tileset data
        palette = self.mainApplication.projectData.palettes[self.currentPaletteIndex].palette
        tileset = self.mainApplication.projectData.tileset.set

        # convert palette to 32bit ARGB (Alpha, Red, Green, Blue)
        npPalette = numpy.array([
            # 1st color in palette is transparent
            ((0x00 if i == 0 else 0xFF) << 24) | (c.red << 16) | (c.green << 8) | c.blue
            for i, c in enumerate(palette)
        ], dtype=numpy.uint32)

        # access raw image buffer
        pointer = self.image.bits()
        pointer.setsize(width * height * 4)
        imageArray = numpy.ndarray((height, width), dtype=numpy.uint32, buffer=pointer)

        # draw tiles into the numpy buffer
        for i, tile in enumerate(tileset):
            y = i * 8
            tileData = npPalette[numpy.array(tile, dtype=numpy.uint8)]
            imageArray[y:y+8, :8] = tileData
        
        self.img = qtg.QPixmap.fromImage(self.image)
        self.pixmapItem.setPixmap(self.img)

class TilePanel(qtw.QWidget):
    """ Panel to select tile and tile properties. """
    # signal to share new properties
    itemsSelected = qtc.pyqtSignal(bool, int, bool, bool) # priority, palette, hflip, vflip

    def __init__(self, mainApplication: object):
        super().__init__()

        # set the tile picker
        self.picker = TilePicker(50, mainApplication)

        # define the attribute buttons
        self.priorityButton = qtw.QPushButton("Priority", self)
        self.paletteButton = qtw.QPushButton("Palette", self)
        self.hFlipButton = qtw.QPushButton("Horizontal Flip", self)
        self.vFlipButton = qtw.QPushButton("Vertical Flip", self)

        # define tile picker layout
        pickerLayout = qtw.QVBoxLayout()
        pickerLayout.addWidget(qtw.QLabel("Tile Select"))
        pickerLayout.addWidget(self.picker)
        pickerLayout.addStretch()

        # define tile attribute layout
        attributeLayout = qtw.QVBoxLayout()
        attributeLayout.addWidget(qtw.QLabel("\tTile Attributes"))
        attributeLayout.addWidget(self.priorityButton)
        attributeLayout.addWidget(self.paletteButton)
        attributeLayout.addWidget(self.hFlipButton)
        attributeLayout.addWidget(self.vFlipButton)
        attributeLayout.addStretch()

        # define central layout
        layout = qtw.QHBoxLayout(self)
        layout.addLayout(pickerLayout)
        layout.addLayout(attributeLayout)

        # define width
        self.setFixedWidth(340)

        # link choosing items to setting properties
        self.itemsSelected.connect(self.picker.SetProperties)

class ChunksetPanel(qtw.QGraphicsView):
    """ Panel allowing you to edit chunksets. """

    def SetTile(self, tileIndex):
        """ Change the current selected tile. """
        self.currentTileIndex = tileIndex
    
    def ResetImage(self):
        """ Redraw the image. """

class ChunksetEditor(qtw.QWidget):
    """ Editor menu allowing you to edit the project's tileset. """
    def __init__(self, mainApplication: object):
        super().__init__()

        # define layout
        layout = qtw.QHBoxLayout(self)

        # vertical line that seperates panels
        separator = qtw.QFrame()
        separator.setFrameShape(qtw.QFrame.Shape.VLine)
        separator.setFrameShadow(qtw.QFrame.Shadow.Sunken)
        separator.setLineWidth(2)

        # define panels
        self.tilePanel = TilePanel(mainApplication)
        self.chunksetPanel = ChunksetPanel(mainApplication)

        # connect color signal
        self.tilePanel.picker.tileSelected.connect(self.chunksetPanel.SetTile)

        # add the panels
        layout.addWidget(self.tilePanel)
        layout.addWidget(separator)
        layout.addWidget(self.chunksetPanel)
