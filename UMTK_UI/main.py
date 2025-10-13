"""Application bootstrap: wires logic and GUI layers."""

from PyQt6 import QtCore, QtWidgets

from pathlib import Path
import sys

from lib.umtk_logic import UMTKLogic
from lib.umtk_gui import UMTKWindow, resource_path


def main():
    # Default to dark theme
    theme = "dark"
    app = QtWidgets.QApplication(sys.argv)
    logic = UMTKLogic()
    window = UMTKWindow(logic=logic, theme=theme)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()