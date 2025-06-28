# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

# for common gui items
from . import common

# for rounding
import math

# for direct image manipulation
import numpy

class ColorPicker(qtw.QLabel):
    """ Colorpicker to select colors from any palette palette. """
    # signal to share color
    colorSelected = qtc.pyqtSignal(int, int) # palette, color index

    def __init__(self, scale: int, mainApplication: object):
        super().__init__()

        # define globals
        self.scale = scale
        self.mainApplication = mainApplication

        # define the palette choice img
        self.img = qtg.QPixmap(4 * scale, 16 * scale)
        self.img.fill(qtg.QColor(0, 0, 0)) # fill with black

        # create selection overlay
        self.overlay = qtg.QPixmap(4 * scale, 16 * scale)
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent
        self.DrawSelect((0, 0))

        # fix the size
        self.setFixedSize(self.img.size())

    def mousePressEvent(self, event):
        """ Get color at click event. """
        # get the click position
        clickPos = event.position().toPoint()
        x, y = clickPos.x(), clickPos.y()

        # select
        self.DrawSelect(((x // self.scale) * self.scale, (y // self.scale) * self.scale))
        self.update()

        # emit color signal
        self.colorSelected.emit((x // self.scale), (y // self.scale))

    def DrawSelect(self, pos: tuple[int, int]):
        """ Draw the selection rectangles. """
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent
        painter = qtg.QPainter(self.overlay)
        painter.setPen(qtg.QPen(qtg.QColor(255, 0, 0), 5)) # color, width
        painter.drawRect(qtc.QRect(pos[0], 0, self.scale, self.scale * 16)) # draw for palette
        painter.drawRect(qtc.QRect(pos[0], pos[1], self.scale, self.scale)) # draw for individual color
        painter.end()
    
    def paintEvent(self, event):
        """ Merge the two pixmaps. """
        painter = qtg.QPainter(self)
        painter.drawPixmap(0, 0, self.img)
        painter.drawPixmap(0, 0, self.overlay)
        painter.end()
    
    def ResetImage(self):
        """ Reset the colors for the color picker image. """
        # define painter
        painter = qtg.QPainter(self.img)

        self.img.fill(qtg.QColor(0, 0, 0))

        # repeat for every palette
        for x, pal in enumerate(self.mainApplication.projectData.palettes):
            # repeat for every color
            for y, col in enumerate(pal.palette):
                painter.setBrush(qtg.QBrush(qtg.QColor(col.red, col.green, col.blue)))
                painter.drawRect(x * self.scale, y * self.scale, self.scale, self.scale)
        
        # finish
        painter.end()
        self.update()

class ColorPanel(qtw.QWidget):
    """ Panel to select colors from any palette palette. """
    def __init__(self, mainApplication: object):
        super().__init__()

        # set the color picker
        self.picker = ColorPicker(50, mainApplication)

        # define layout
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(qtw.QLabel("Color Select"))
        layout.addWidget(self.picker)
        layout.addStretch()

        # define width
        self.setFixedWidth(340)

class TilesetPanel(qtw.QGraphicsView):
    """ Panel allowing you to edit tilemaps. """
    # signal for change in tile
    tileChange = qtc.pyqtSignal()

    def __init__(self, mainApplication: object):
        super().__init__()

        # define constants
        self.mainApplication = mainApplication
        self.background = qtg.QPixmap("resources/images/transparentBackground.png").scaled(4040, 4040)

        # scene/image init
        self.graphicsScene = qtw.QGraphicsScene()
        self.setScene(self.graphicsScene)

        # pixmap
        self.pixmap = qtg.QPixmap(32 * 8, 64 * 8)
        self.pixmap.fill(qtg.QColor(0, 0, 0, 0))
        self.pixmapItem = self.graphicsScene.addPixmap(self.pixmap)

        # draw a grid ontop of the pixmap
        self.graphicsScene.addItem(common.GridOverlay((self.pixmap.width(), self.pixmap.height()), 8))

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

        # set palette/color default
        self.currentPaletteIndex = 0
        self.currentColorIndex = 0
    
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
            self.DrawPixels(event) # draw colors
    
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
            self.DrawPixels(event) # draw colors
    
    def mouseReleaseEvent(self, event):
        """ When the mouse is let go. """
        # send tilechange signal
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            self.tileChange.emit()
    
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
    
    def SetColor(self, paletteIndex: int, colorIndex: int):
        """ Set the color and the palette. """
        if self.currentPaletteIndex != paletteIndex: # if new palette redraw the image
            self.currentPaletteIndex = paletteIndex
            self.ResetImage()
        self.currentColorIndex = colorIndex
    
    def DrawPixels(self, event: qtg.QMouseEvent):
        """ Draw pixels at event location. """
        # get the coords within the pixmap
        coords = (
            math.floor(self.pixmapItem.mapFromScene(self.mapToScene(event.position().toPoint())).x()),
            math.floor(self.pixmapItem.mapFromScene(self.mapToScene(event.position().toPoint())).y())
        )

        # check if out of range
        if not (0 <= coords[0] < self.pixmap.width() and 0 <= coords[1] < self.pixmap.height()):
            return
        
        # get the color
        color = self.mainApplication.projectData.palettes[self.currentPaletteIndex].GetColor(self.currentColorIndex)
        qColor = qtg.QColor(color.red, color.green, color.blue, 255)

        # get index in tileset
        tileX, tileY = coords[0] // 8, coords[1] // 8
        tilesPerRow = self.pixmap.width() // 8
        tileIndex = (tileY * tilesPerRow) + tileX

        if tileIndex + 1 > self.mainApplication.projectData.tileset.size:
            return

        # get x/y within tile
        x, y = coords[0] % 8, coords[1] % 8

        # edit the tile
        self.mainApplication.projectData.tileset.set[tileIndex][y][x] = self.currentColorIndex

        # draw the color
        image = self.pixmap.toImage()
        if self.currentColorIndex == 0:
            # if the color is 0 than make transparent
            image.setPixelColor(coords[0], coords[1], qtg.QColor(0, 0, 0, 0))
        else:
            # otherwise painter regular color
            image.setPixelColor(coords[0], coords[1], qColor)
        self.pixmap = qtg.QPixmap.fromImage(image)
        self.pixmapItem.setPixmap(self.pixmap) # update pixmap

    def ResetImage(self):
        """ Redraw the image. """
        # create blank image
        width = self.pixmap.width()
        height = self.pixmap.height()
        image = qtg.QImage(width, height, qtg.QImage.Format.Format_ARGB32)

        # grab palette/tileset data
        palette = self.mainApplication.projectData.palettes[self.currentPaletteIndex].palette
        tileset = self.mainApplication.projectData.tileset.set
        tilesPerRow = width // 8

        # convert palette to 32bit ARGB (Alpha, Red, Green, Blue)
        npPalette = numpy.array([
            # 1st color in palette is transparent
            ((0x00 if i == 0 else 0xFF) << 24) | (c.red << 16) | (c.green << 8) | c.blue
            for i, c in enumerate(palette)
        ], dtype=numpy.uint32)

        # access raw image buffer
        pointer = image.bits()
        pointer.setsize(width * height * 4)
        imageArray = numpy.ndarray((height, width), dtype=numpy.uint32, buffer=pointer)

        # draw tiles into the numpy buffer
        for tileIndex, tile in enumerate(tileset):
            # convert tile index into x/y
            tileX, tileY = (tileIndex % tilesPerRow) * 8, (tileIndex // tilesPerRow) * 8

            # loop for every row in tile
            for y in range(8):
                row = tile[y]
                # loop for every collumn in tile
                for x in range(8):
                    imageArray[tileY + y, tileX + x] = npPalette[row[x]]
        
        # convert back to pixmap and update pixmap item
        self.pixmap = qtg.QPixmap.fromImage(image)
        self.pixmapItem.setPixmap(self.pixmap)

class TilesetEditor(qtw.QWidget):
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
        self.colorPanel = ColorPanel(mainApplication)
        self.tilesetPanel = TilesetPanel(mainApplication)

        # connect color signal
        self.colorPanel.picker.colorSelected.connect(self.tilesetPanel.SetColor)

        # add the panels
        layout.addWidget(self.colorPanel)
        layout.addWidget(separator)
        layout.addWidget(self.tilesetPanel)
