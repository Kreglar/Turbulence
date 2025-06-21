# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

class GridOverlay(qtw.QGraphicsItem):
    """ Grid overlay. """
    def __init__(self, imageSize: tuple[int, int], gridSize: int):
        super().__init__()
        self.imageSize = imageSize
        self.gridSize = gridSize
        self.setZValue(1) # draw on top

    def boundingRect(self): # needs to be overridden
        return qtc.QRectF(0, 0, *self.imageSize)
    
    def paint(self, painter, option, widget = ...):
        """ Paint the grid. """
        # define the pen
        painter.setPen(qtg.QPen(qtg.QColor(255, 255, 255), 0.0))

        # draw vertical gridlines
        for x in range(0, self.imageSize[0] + 1, self.gridSize):
            painter.drawLine(x, 0, x, self.imageSize[1])
        
        # draw horizontal gridlines
        for y in range(0, self.imageSize[1] + 1, self.gridSize):
            painter.drawLine(0, y, self.imageSize[0], y)

class SelectionOverlay(qtw.QGraphicsItem):
    def __init__(self):
        super().__init__()

        # globals
        self.xPos = 0
        self.yPos = 0
        self.width = 0
        self.height = 0

    def PickupSelection(self, pixmap: qtg.QPixmap):
        pass
