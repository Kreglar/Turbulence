# Turbulence
# Made With LOVE by kreglar XOXOXOXO!!
# Version 0.0.0 - Unreleased

# gui
from PyQt6 import QtWidgets as qtw

# command line arguments
import sys

# main application
import app

if __name__ == "__main__":
    main = qtw.QApplication(sys.argv) # create main application instance
    gui = app.Application() # create gui instance
    gui.show() # show the gui
    sys.exit(main.exec()) # exit the application
