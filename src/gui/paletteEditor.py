# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

# custom data formats
from utils import data

# for common gui items
from . import common

class ColorPicker(qtw.QLabel):
    """ 512 color picker with mouse events. """
    # signal to share color
    colorSelected = qtc.pyqtSignal(qtg.QColor)

    def __init__(self, imgPath: str, scale: int):
        super().__init__()

        # get essential variables
        rawimg = qtg.QPixmap(imgPath)
        self.scale = scale

        # set image pixmap
        self.img = rawimg.scaled(rawimg.size().width() * scale, rawimg.size().height() * scale)

        # create selection overlay
        self.overlay = qtg.QPixmap(rawimg.size().width() * scale, rawimg.size().height() * scale)
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

        # get the pixel at the clicks
        qColor = self.img.toImage().pixelColor(x, y)
        self.colorSelected.emit(qColor)

    def DrawSelect(self, pos: tuple[int, int]):
        """ Draw the selection rectangle. """
        self.overlay.fill(qtg.QColor(0, 0, 0, 0)) # fill tranasparent
        painter = qtg.QPainter(self.overlay)
        painter.setPen(qtg.QPen(qtg.QColor(255, 0, 0), 5)) # color, width
        painter.drawRect(qtc.QRect(pos[0], pos[1], self.scale, self.scale))
        painter.end()
    
    def paintEvent(self, event):
        """ Merge the two pixmaps. """
        painter = qtg.QPainter(self)
        painter.drawPixmap(0, 0, self.img)
        painter.drawPixmap(0, 0, self.overlay)
        painter.end()

class ColorPanel(qtw.QWidget):
    """ Palette editor color select. """
    def __init__(self):
        super().__init__()

        # set the color picker
        self.picker = ColorPicker("resources/images/colorPicker.png", 20)

        # define layout
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(qtw.QLabel("Color Select"))
        layout.addWidget(self.picker)
        layout.addStretch()

        # define width
        self.setFixedWidth(340)

class PaletteVisual(qtw.QLabel):
    """ Visualization of a palette. """
    # signal for change in palette
    paletteChange = qtc.pyqtSignal()

    def __init__(self, scale: int, mainApplication: object, paletteNum: int):
        super().__init__()

        # set globals
        self.scale = scale
        self.mainApplication = mainApplication
        self.paletteNum = paletteNum
        self.dragStart = qtc.QPoint()

        # define the palette's img
        self.img = qtg.QPixmap(16 * scale, scale)
        self.img.fill(qtg.QColor(0, 0, 0)) # fill with black

        # make the widget the same size as the image
        self.setFixedSize(self.img.size())

        # default color is black
        self.currentColor = qtg.QColor(0, 0, 0)
    
    def setColor(self, color: qtg.QColor):
        """ Receive the signal and change the color. """
        self.currentColor = color
    
    def mousePressEvent(self, event):
        """ Get color at click event. """
        # left mouse click
        if event.button() == qtc.Qt.MouseButton.LeftButton:
            # get the click position
            clickPos = event.position().toPoint()
            x = clickPos.x() // self.scale

            # set the current color
            color = data.Color(self.currentColor.red(), self.currentColor.green(), self.currentColor.blue())
            self.mainApplication.projectData.palettes[self.paletteNum].AddColor(color, x)
            # draw the color
            painter = qtg.QPainter(self.img)
            painter.setBrush(qtg.QBrush(self.currentColor))
            painter.drawRect(x * self.scale, 0, self.scale, self.scale)
            painter.end()
            self.update()

            # send the palette change signal
            self.paletteChange.emit()
    
    def paintEvent(self, event):
        """ Draw the new pixmap. """
        painter = qtg.QPainter(self)
        painter.drawPixmap(0, 0, self.img)
        painter.end()

class PalettePanel(qtw.QWidget):
    """ Palette editor palette view/edit. """
    def __init__(self, mainApplication: object):
        super().__init__()

        # palette visuals
        self.visuals = [
            PaletteVisual(75, mainApplication, 0),
            PaletteVisual(75, mainApplication, 1),
            PaletteVisual(75, mainApplication, 2),
            PaletteVisual(75, mainApplication, 3)
        ]

        # define layout
        layout = qtw.QVBoxLayout(self)
        layout.addWidget(qtw.QLabel("Palette View"))
        layout.addWidget(self.visuals[0])
        layout.addWidget(self.visuals[1])
        layout.addWidget(self.visuals[2])
        layout.addWidget(self.visuals[3])
        layout.addStretch()

class PaletteEditor(qtw.QWidget):
    """ Editor menu allowing you to edit the project's palettes. """
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
        self.colorPanel = ColorPanel()
        self.palettePanel = PalettePanel(mainApplication)

        # connct signals with setting the brush color
        for pv in self.palettePanel.visuals:
            self.colorPanel.picker.colorSelected.connect(pv.setColor)

        # add the panels
        layout.addWidget(self.colorPanel)
        layout.addWidget(separator)
        layout.addWidget(self.palettePanel)
