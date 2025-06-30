# gui
from PyQt6 import QtWidgets as qtw, QtGui as qtg, QtCore as qtc

class MenuBar(qtw.QMenuBar):
    """ Menubar gui object. """
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
                "Export": ["Palette", "Tileset", "Chunkset", "Tilemap"]
                },
                None,
                "Quit"
            ],
            "Edit": ["Undo", "Redo"],
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
                            action.triggered.connect(lambda connect, s=[menuName, subMenuName, subOption]: self.ButtonFunc(s))
                            subMenu.addAction(action)
                    else: # the item is not a submenu
                        action = qtg.QAction(option, self)
                        action.triggered.connect(lambda connect, s=[menuName, option]: self.ButtonFunc(s))
                        menu.addAction(action)
                else: # the option is None (separator)
                    menu.addSeparator()
    
    def ButtonFunc(self, button: list):
        """ What to do when a menu button is pressed. """
        if button == ["File", "Open"]: # opening a file
            self.mainApplication.LoadProjectFile()

        elif button == ["File", "Save"]: # saving a file
            self.mainApplication.SaveProjectFile()

        elif button == ["File", "Save As"]: # saving anew file
            self.mainApplication.SaveNewProjectFile()
        
        elif button[0:2] == ["File", "Import"]:
            self.mainApplication.ImportFile(button[2])
        
        elif button[0:2] == ["File", "Export"]:
            pass
