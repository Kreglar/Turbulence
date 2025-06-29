# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

# for common gui items
from . import common

# for custom data types
from utils import data

# for rounding
import math

# for direct image manipulation
import numpy

class ChunkPicker(qtw.QGraphicsView):
    """ Chunkpicker used to select chunk. """
    # signal to share chunk
    selectedChunk = qtc.pyqtSignal(int)

    def __init__(self, scale: int, mainApplication: object):
        super().__init__()

        # define globals
        self.imgScale = scale
        self.mainApplication = mainApplication
        self.chunkset = mainApplication.projectData.chunkset
        self.currentHFlip = False
        self.currentVFlip = False

        # scene/image init
        self.graphicsScene = qtw.QGraphicsScene()
        self.setScene(self.graphicsScene)

        # define the tile choice img
        self.img = qtg.QPixmap(8 * self.chunkset.chunkSize, self.chunkset.size * 8 * self.chunkset.chunkSize)
        self.img.fill(qtg.QColor(0, 0, 0)) # fill with black

        # create the label holding the img
        self.pixmapItem = self.graphicsScene.addPixmap(self.img)

        # create selection overlay
        self.overlay = qtg.QPixmap(8 * self.chunkset.chunkSize, self.chunkset.size * 8 * self.chunkset.chunkSize)
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
        self.scale(self.imgScale // (8 * self.chunkset.chunkSize), self.imgScale // (8 * self.chunkset.chunkSize))
    
    def mousePressEvent(self, event):
        """ Get tile at click event. """
        # get the click position
        y = (event.position().toPoint().y() + self.verticalScrollBar().value()) // self.imgScale

        # select
        self.DrawSelect(y)

        # emit color signal
        self.selectedChunk.emit(y)
    
    def DrawSelect(self, pos: int):
        """ Draw the selection outline at pos tile. """
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent
        painter = qtg.QPainter(self.overlay)
        painter.setPen(qtg.QPen(qtg.QColor(255, 0, 0), 1)) # color, width
        painter.drawRect(qtc.QRect(0, pos * (8 * self.chunkset.chunkSize), (8 * self.chunkset.chunkSize), (8 * self.chunkset.chunkSize))) # draw for outline
        painter.end()
        self.overlayItem.setPixmap(self.overlay) # add the new pixmap
    
    def SetProperties(self, hFlip: bool, vFlip: bool):
        """ Set the properties of what is selected. """
        self.currentHFlip = hFlip
        self.currentVFlip = vFlip

        # redraw the image
        self.ResetImage()

    def ResetImage(self):
        """ Redraw the image. """
        # create blank image
        width = self.img.width()
        height = self.img.height()

        # get data
        palettes = self.mainApplication.projectData.palettes
        tileset = self.mainApplication.projectData.tileset.set[:]
        chunkset = self.mainApplication.projectData.chunkset.set[:]

        # convert palette to 32bit ARGB (Alpha, Red, Green, Blue)
        npPalettes = [numpy.array([
            # 1st color in palette is transparent
            ((0x00 if i == 0 else 0xFF) << 24) | (c.red << 16) | (c.green << 8) | c.blue
            for i, c in enumerate(pal.palette)
        ], dtype=numpy.uint32) for pal in palettes]

        # access raw image buffer
        pointer = self.image.bits()
        pointer.setsize(width * height * 4)
        imageArray = numpy.ndarray((height, width), dtype=numpy.uint32, buffer=pointer)

        # draw tiles into the numpy buffer
        for i, c in enumerate(chunkset):
            chunk = c[:] # fixes reference problems

            # apply flips based on flags
            if self.currentHFlip:
                for row in range(self.chunkset.chunkSize):
                    chunk[row] = chunk[row][::-1] # flip each row within the chunk
            if self.currentVFlip:
                chunk = chunk[::-1] # flip the chunk data horizontally

            # add each tile
            for y in range(self.chunkset.chunkSize):
                for x in range(self.chunkset.chunkSize):
                    # get the tile as an object
                    tileObject = chunk[y][x]

                    # create 2d array for tile
                    tile = tileset[tileObject.id]
                    tileData = npPalettes[tileObject.palette][numpy.array(tile, dtype=numpy.uint8)]

                    # apply flips based on flags
                    if tileObject.hFlip:
                        for row in range(8):
                            tileData[row] = tileData[row][::-1] # flip each row within the tile
                    if tileObject.vFlip:
                        tileData = tileData[::-1] # flip the tile data horizontally

                    tileX, tileY = x * 8, (y * 8) + (i * 8 * self.chunkset.chunkSize)

                    imageArray[tileY:tileY+8, tileX:tileX+8] = tileData
        
        self.img = qtg.QPixmap.fromImage(self.image)
        self.pixmapItem.setPixmap(self.img)

class ChunkPanel(qtw.QWidget):
    """ Panel to select chunk and chunk properties. """
    # signal to share new properties
    itemsSelected = qtc.pyqtSignal(bool, bool) # hflip, vflip

    def __init__(self, mainApplication: object):
        super().__init__()

        # set the tile picker
        self.picker = ChunkPicker(64, mainApplication)

        # define the attribute buttons
        self.hFlipButton = qtw.QPushButton("Horizontal Flip", self)
        self.vFlipButton = qtw.QPushButton("Vertical Flip", self)

        # make buttons toggleable
        self.hFlipButton.setCheckable(True)
        self.vFlipButton.setCheckable(True)

        # link buttons to color change
        self.hFlipButton.clicked.connect(self.hFlipButtonPressed)
        self.hFlipButtonPressed()
        self.vFlipButton.clicked.connect(self.vFlipButtonPressed)
        self.vFlipButtonPressed()

        # define chunk picker layout
        pickerLayout = qtw.QVBoxLayout()
        pickerLayout.addWidget(qtw.QLabel("Chunk Select"))
        pickerLayout.addWidget(self.picker)
        pickerLayout.addStretch()

        # define chunk attribute layout
        attributeLayout = qtw.QVBoxLayout()
        attributeLayout.addWidget(qtw.QLabel("\tChunk Attributes"))
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
        self.itemsSelected.emit(self.hFlipButton.isChecked(), self.vFlipButton.isChecked())

class TilemapPanel(qtw.QGraphicsView):
    """ Panel allowing you to edit the tilemap. """
    def __init__(self, mainApplication: object):
        super().__init__()

        # define constants
        self.mainApplication = mainApplication
        self.background = qtg.QPixmap("resources/images/transparentBackground.png").scaled(4040, 4040)
        self.mapSize = mainApplication.projectData.tilemap.size
        self.chunkset = mainApplication.projectData.chunkset
        self.currentChunkIndex = 0
        self.currentHFlip = False
        self.currentVFlip = False

        # scene/image init
        self.graphicsScene = qtw.QGraphicsScene()
        self.setScene(self.graphicsScene)

        # pixmap
        self.pixmap = qtg.QPixmap(self.mapSize[0] * self.chunkset.chunkSize * 8, self.mapSize[1] * self.chunkset.chunkSize * 8)
        self.pixmap.fill(qtg.QColor(0, 0, 0, 0))
        self.pixmapItem = self.graphicsScene.addPixmap(self.pixmap)

        # draw a grid ontop of the pixmap
        self.graphicsScene.addItem(common.GridOverlay((self.pixmap.width(), self.pixmap.height()), 8 * self.chunkset.chunkSize))

        # set scroll area and center
        self.setSceneRect(-5000, -5000, 10000, 10000)
        self.centerOn(self.pixmapItem)

        # for zoom/scroll
        self._lastPos = qtc.QPoint()
        self.zoom = 1.0

        # allways show scroll bar and set transform/resize anchors
        self.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setTransformationAnchor(qtw.QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(qtw.QGraphicsView.ViewportAnchor.NoAnchor)
    
    def drawBackground(self, painter: qtg.QPainter, rect):
        """ Draws a non-scrolling background. """
        painter.resetTransform() # cancel zoom/pan so it doesn't scroll background
        painter.drawPixmap(0, 0, self.background) # draws the background at (0, 0)

    def mousePressEvent(self, event):
        """ When the mouse is pressed down. """
        # right mouse click
        if event.button() == qtc.Qt.MouseButton.RightButton:
            # start panning
            self._lastPos = event.position().toPoint() # set new mouse pos

        # left mouse click
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            self.DrawChunks(event) # draw colors
    
    def mouseMoveEvent(self, event):
        """ When the mouse is moved. """
        # scroll image
        if event.buttons() & qtc.Qt.MouseButton.RightButton:
            delta = event.position().toPoint() - self._lastPos # get change between last and current mouse pos
            self._lastPos = event.position().toPoint() # set new mouse pos

            # change x/y scroll values
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())

        # left mouse click
        if event.buttons() & qtc.Qt.MouseButton.LeftButton:
            self.DrawChunks(event) # draw colors
    
    def wheelEvent(self, event):
        """ When the mouse is scrolled. """
        # get scroll amount
        angle = event.angleDelta().y()
        if angle == 0:
            return
            
        # zoom logic
        zoomIn = angle > 0
        zoomFactor = 1.15 if zoomIn else 1 / 1.15
        self.zoom *= zoomFactor

        # scale image centered on cursor
        oldPos = self.mapToScene(event.position().toPoint())
        self.scale(zoomFactor, zoomFactor)
        newPos = self.mapToScene(event.position().toPoint())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def SetChunk(self, chunkIndex):
        """ Change the current selected chunk. """
        self.currentChunkIndex = chunkIndex
    
    def SetProperties(self, hFlip: bool, vFlip: bool):
        """ Set the properties of what is selected. """
        self.currentHFlip = hFlip
        self.currentVFlip = vFlip
    
    def DrawChunks(self, event: qtg.QMouseEvent):
        """ Draw tiles at event location. """
        # get the coords within the pixmap
        coords = (
            math.floor(self.pixmapItem.mapFromScene(self.mapToScene(event.position().toPoint())).x()),
            math.floor(self.pixmapItem.mapFromScene(self.mapToScene(event.position().toPoint())).y())
        )

        # check if out of range
        if not (0 <= coords[0] < self.pixmap.width() and 0 <= coords[1] < self.pixmap.height()):
            return
        
        # get coords within tilemap
        withinX = coords[0] // (8 * self.chunkset.chunkSize)
        withinY = coords[1] // (8 * self.chunkset.chunkSize)

        # apply to tilemap
        self.mainApplication.projectData.tilemap.map[withinY][withinX] = data.Chunk(self.currentChunkIndex, self.currentHFlip, self.currentVFlip)
        
        # get the chunk data
        chunkArray = self.mainApplication.projectData.chunkset.set[self.currentChunkIndex][:]

        # apply flips
        if self.currentHFlip:
            for y in range(self.chunkset.chunkSize):
                chunkArray[y] = chunkArray[y][::-1]
        if self.currentVFlip:
            chunkArray = chunkArray[::-1]

        # create pixmap image
        pixmapImage = self.pixmap.toImage()

        # get data
        palettes = self.mainApplication.projectData.palettes
        tileset = self.mainApplication.projectData.tileset.set[:]

        # convert palette to 32bit ARGB (Alpha, Red, Green, Blue)
        npPalettes = [numpy.array([
            # 1st color in palette is transparent
            ((0x00 if i == 0 else 0xFF) << 24) | (c.red << 16) | (c.green << 8) | c.blue
            for i, c in enumerate(pal.palette)
        ], dtype=numpy.uint32) for pal in palettes]

        # access raw image buffer
        pointer = pixmapImage.bits()
        pointer.setsize(self.pixmap.width() * self.pixmap.height() * 4)
        imageArray = numpy.ndarray((self.pixmap.height(), self.pixmap.width()), dtype=numpy.uint32, buffer=pointer)

        # add each tile
        for y in range(self.chunkset.chunkSize):
            for x in range(self.chunkset.chunkSize):
                # get the tile as an object
                tileObject = chunkArray[y][x]

                # create 2d array for tile
                tile = tileset[tileObject.id]
                tileData = npPalettes[tileObject.palette][numpy.array(tile, dtype=numpy.uint8)]

                # apply flips based on flags
                if tileObject.hFlip:
                    for row in range(8):
                        tileData[row] = tileData[row][::-1] # flip each row within the tile
                if tileObject.vFlip:
                    tileData = tileData[::-1] # flip the tile data horizontally

                # get coords of tile
                tileX = x * 8 + ((coords[0] // (self.chunkset.chunkSize * 8)) * (self.chunkset.chunkSize * 8))
                tileY = y * 8 + ((coords[1] // (self.chunkset.chunkSize * 8)) * (self.chunkset.chunkSize * 8))

                # draw the tile
                imageArray[tileY:tileY+8, tileX:tileX+8] = tileData

        # convert back to pixmap and update pixmap item
        self.pixmap = qtg.QPixmap.fromImage(pixmapImage)
        self.pixmapItem.setPixmap(self.pixmap)
    
    def ResetImage(self):
        """ Redraw the image. """
        # create blank image
        width = self.pixmap.width()
        height = self.pixmap.height()
        image = qtg.QImage(width, height, qtg.QImage.Format.Format_ARGB32)

        # grab palette/tileset/chunkset/tilemap data
        palettes = self.mainApplication.projectData.palettes
        tileset = self.mainApplication.projectData.tileset.set
        chunkset = self.mainApplication.projectData.chunkset.set
        tilemap = self.mainApplication.projectData.tilemap.map

        # convert palettes to 32bit ARGB (Alpha, Red, Green, Blue)
        npPalettes = [numpy.array([
            # 1st color in palette is transparent
            ((0x00 if i == 0 else 0xFF) << 24) | (c.red << 16) | (c.green << 8) | c.blue
            for i, c in enumerate(pal.palette)
        ], dtype=numpy.uint32) for pal in palettes]

        # access raw image buffer
        pointer = image.bits()
        pointer.setsize(width * height * 4)
        imageArray = numpy.ndarray((height, width), dtype=numpy.uint32, buffer=pointer)

        for chunkY in range(self.mapSize[1]):
            for chunkX in range(self.mapSize[0]):
                # get chunk data
                chunkObject = tilemap[chunkY][chunkX]
                chunkArray = chunkset[chunkObject.id][:]

                # apply flips
                if chunkObject.hFlip:
                    for y in range(self.chunkset.chunkSize):
                        chunkArray[y] = chunkArray[y][::-1]
                if chunkObject.vFlip:
                    chunkArray = chunkArray[::-1]
                
                # add each tile
                for y in range(self.chunkset.chunkSize):
                    for x in range(self.chunkset.chunkSize):
                        # get the tile as an object
                        tileObject = chunkArray[y][x]

                        # create 2d array for tile
                        tile = tileset[tileObject.id]
                        tileData = npPalettes[tileObject.palette][numpy.array(tile, dtype=numpy.uint8)]

                        # apply flips based on flags
                        if tileObject.hFlip:
                            for row in range(8):
                                tileData[row] = tileData[row][::-1] # flip each row within the tile
                        if tileObject.vFlip:
                            tileData = tileData[::-1] # flip the tile data horizontally

                        tileX, tileY = (chunkX * self.chunkset.chunkSize * 8) + (x * 8), (chunkY * self.chunkset.chunkSize * 8) + (y * 8)
                        imageArray[tileY:tileY+8, tileX:tileX+8] = tileData
        
        # convert image to pixmap and apply
        self.pixmap = qtg.QPixmap.fromImage(image)
        self.pixmapItem.setPixmap(self.pixmap)

class TilemapEditor(qtw.QWidget):
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
        self.chunkPanel = ChunkPanel(mainApplication)
        self.tilemapPanel = TilemapPanel(mainApplication)

        # connect signals
        self.chunkPanel.itemsSelected.connect(self.tilemapPanel.SetProperties)
        self.chunkPanel.picker.selectedChunk.connect(self.tilemapPanel.SetChunk)

        # add the panels
        layout.addWidget(self.chunkPanel)
        layout.addWidget(separator)
        layout.addWidget(self.tilemapPanel)
