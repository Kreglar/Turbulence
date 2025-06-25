# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

# for common gui items
from . import common

# for rounding
import math

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
        self.overlay = qtg.QPixmap(8, self.tileset.size * 8)
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent
        self.overlayItem = self.graphicsScene.addPixmap(self.overlay)
        self.DrawSelect(0)

        # fix the size
        self.setFixedSize(scale + 16, scale * 13) # +16 makes room for the scroll bar

        # always have vertical scroll bar
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        # create image once to edit later
        width = self.img.width()
        height = self.img.height()
        self.image = qtg.QImage(width, height, qtg.QImage.Format.Format_ARGB32)

        # set the scale
        self.resetTransform()
        self.scale(self.imgScale // 8, self.imgScale // 8)
    
    def mousePressEvent(self, event):
        """ Get tile at click event. """
        # get the click position
        y = (event.position().toPoint().y() + self.verticalScrollBar().value()) // self.imgScale

        # select
        self.DrawSelect(y)

        # emit color signal
        self.tileSelected.emit(y)
    
    def DrawSelect(self, pos: int):
        """ Draw the selection outline at pos tile. """
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent
        painter = qtg.QPainter(self.overlay)
        painter.setPen(qtg.QPen(qtg.QColor(255, 0, 0), 1)) # color, width
        painter.drawRect(qtc.QRect(0, pos * 8, 8, 8)) # draw for outline
        painter.end()
        self.overlayItem.setPixmap(self.overlay) # add the new pixmap
    
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
            
            # apply flips based on flags
            if self.currentHFlip and i == 0:
                for row in range(8):
                    tileData[row] = tileData[row][::-1] # flip each row within the tile
            if self.currentVFlip:
                tileData = tileData[::-1] # flip the tile data horizontally

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
        self.picker = TilePicker(64, mainApplication)

        # define the attribute buttons
        self.priorityButton = qtw.QPushButton("Priority", self)
        self.paletteButton = qtw.QPushButton("Palette", self)
        self.hFlipButton = qtw.QPushButton("Horizontal Flip", self)
        self.vFlipButton = qtw.QPushButton("Vertical Flip", self)

        # make buttons toggleable
        self.priorityButton.setCheckable(True)
        self.hFlipButton.setCheckable(True)
        self.vFlipButton.setCheckable(True)

        # link buttons to color change
        self.priorityButton.clicked.connect(self.PriorityButtonPressed)
        self.PriorityButtonPressed()
        self.hFlipButton.clicked.connect(self.hFlipButtonPressed)
        self.hFlipButtonPressed()
        self.vFlipButton.clicked.connect(self.vFlipButtonPressed)
        self.vFlipButtonPressed()

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
    
    def PriorityButtonPressed(self):
        """ Priority button is toggled. """
        # see if button checked or not
        if self.priorityButton.isChecked():
            # the button just go checked
            self.priorityButton.setText("High Priority")
            self.priorityButton.setStyleSheet("background-color: green;")
        else:
            # the button just got unchecked
            self.priorityButton.setText("Low Priority")
            self.priorityButton.setStyleSheet("background-color: red;")
        
        # emit
        self.EmitAttributes()
    
    def hFlipButtonPressed(self):
        """ Horizontal flip button is toggled. """
        # see if button checked or not
        if self.hFlipButton.isChecked():
            # the button just go checked
            self.hFlipButton.setText("Horizontal Flip")
            self.hFlipButton.setStyleSheet("background-color: green;")
        else:
            # the button just got unchecked
            self.hFlipButton.setText("No Horizontal Flip")
            self.hFlipButton.setStyleSheet("background-color: red;")
        
        # emit
        self.EmitAttributes()
    
    def vFlipButtonPressed(self):
        """ Vertical flip button is toggled. """
        # see if button checked or not
        if self.vFlipButton.isChecked():
            # the button just go checked
            self.vFlipButton.setText("Vertical Flip")
            self.vFlipButton.setStyleSheet("background-color: green;")
        else:
            # the button just got unchecked
            self.vFlipButton.setText("No Vertical Flip")
            self.vFlipButton.setStyleSheet("background-color: red;")

        # emit
        self.EmitAttributes()
    
    def EmitAttributes(self):
        """ Emit all the attributes of the tile selection. """
        self.itemsSelected.emit(self.priorityButton.isChecked(), 0, self.hFlipButton.isChecked(), self.vFlipButton.isChecked())

class ChunksetPanel(qtw.QGraphicsView):
    """ Panel allowing you to edit chunksets. """

    def SetTile(self, tileIndex):
        """ Change the current selected tile. """
        self.currentTileIndex = tileIndex
    
    def SetProperties(self, priority: bool, palette: int, hFlip: bool, vFlip: bool):
        """ Set the properties of what is selected. """
        self.currentPaletteIndex = palette
        self.currentHFlip = hFlip
        self.currentVFlip = vFlip
    
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

        # connect signals
        self.tilePanel.itemsSelected.connect(self.chunksetPanel.SetProperties)
        self.tilePanel.picker.tileSelected.connect(self.chunksetPanel.SetTile)

        # add the panels
        layout.addWidget(self.tilePanel)
        layout.addWidget(separator)
        layout.addWidget(self.chunksetPanel)
