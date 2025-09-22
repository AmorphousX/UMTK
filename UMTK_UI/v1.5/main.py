"""Application bootstrap: wires logic and GUI layers."""

try:
    from PyQt6 import QtCore, QtWidgets  # type: ignore
except ImportError:
    from PySide6 import QtCore, QtWidgets  # type: ignore

from pathlib import Path
import sys

from lib.umtk_logic import UMTKLogic
from lib.umtk_gui import UMTKWindow, resource_path


def load_theme(app, window, theme: str):
    if theme == "Dark":
        file = QtCore.QFile(resource_path("style/Dark.qss"))
    else:
        file = QtCore.QFile(resource_path("style/modern_style.qss"))
    if file.open(QtCore.QFile.OpenModeFlag.ReadOnly | QtCore.QFile.OpenModeFlag.Text):
        stream = QtCore.QTextStream(file)
        qss = stream.readAll()
        app.setStyleSheet(qss)
        window.setStyleSheet(qss)


def main():
    theme = "Dark"
    app = QtWidgets.QApplication(sys.argv)
    logic = UMTKLogic()
    window = UMTKWindow(logic=logic, theme=theme)
    load_theme(app, window, theme)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()