# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

class MenuBar(qtw.QMenuBar):
    """ Menubar gui object. """
    # signal for selected option
    selectedOption = qtc.pyqtSignal(list)

    def __init__(self, mainApplication: qtw.QMainWindow):
        super().__init__(mainApplication)

        self.mainApplication = mainApplication

        # add options
        self.AddOptions()

    def AddOptions(self):
        """ Add all the options. """
        # list of options
        options = {
            "File": [
                "New",
                "Open",
                "Save",
                "Save As",
                None, # use None as a seperator
                {
                "Import": ["Palette", "Tileset", "Chunkset", "Tilemap"]
                },
                {
                "Export": ["All", "Palette", "Tileset", "Chunkset", "Tilemap"]
                },
                None,
                "Quit"
            ],
            "Edit": [],
            "View": []
        }

        # add each option
        for menuName, items in options.items(): # loop over every menu
            menu = self.addMenu(menuName) # create each menu
            for option in items: # loop over every item in current menu
                if option: # if the option is not None (separator)
                    if isinstance(option, dict): # if the item is a submenu
                        subMenuName = list(option.keys())[0] # get the name of the submenu
                        subMenu = menu.addMenu(subMenuName) # create the submenu
                        for subOption in option[subMenuName]: # loop over every item in the submenu
                            action = qtg.QAction(subOption, self)
                            action.triggered.connect(lambda connect, s=[menuName, subMenuName, subOption]: self.selectedOption.emit(s))
                            subMenu.addAction(action)
                    else: # the item is not a submenu
                        action = qtg.QAction(option, self)
                        action.triggered.connect(lambda connect, s=[menuName, option]: self.selectedOption.emit(s))
                        menu.addAction(action)
                else: # the option is None (separator)
                    menu.addSeparator()

class Toolbar(qtw.QToolBar):
    """ Toolbar allowing you to select tools. """
    # signal showing button press

    def __init__(self, mainApplication: object):
        super().__init__()

        # define globals
        self.mainApplication = mainApplication
        self.toolsList = []
        self.selectedTool = ""

        # setup
        self.setMovable(False)
        self.setIconSize(qtc.QSize(16, 16))
        self.setToolButtonStyle(qtc.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # add tools
        self.AddTools()

    def AddTools(self):
        """ Add all the tools. """
        # list of tools
        tools = [
            ("Move", qtg.QIcon("src/assets/moveTool.png")),
            ("Select", qtg.QIcon("src/assets/selectTool.png")),
            ("Brush", qtg.QIcon("src/assets/brushTool.png"))
        ]

        # add each tool
        for t, icon in tools:
            action = qtg.QAction(icon, t, self)
            action.setCheckable(True)
            action.setToolTip(t + " tool")
            action.triggered.connect(lambda checked, tool=t: self.SelectTool(tool))
            self.addAction(action)
            self.toolsList.append(action)
    
    def SelectTool(self, tool: str):
        """ Deselect other tools and emit signal. """
        # deselect other tools
        for t in self.toolsList:
            t.setChecked(t.text() == tool)
        # emit signal
        self.selectedTool = tool
