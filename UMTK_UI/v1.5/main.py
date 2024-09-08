from PyQt6 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from lib.UMTKSerial import UMTKSerial as UMTKSerial_t
import matplotlib.pyplot as plt 
import numpy as np
import random
import copy
import logging
from PyQt6.QtCore import QFile, QTextStream
from qt_material import apply_stylesheet

from lib.umtk_design import Ui_MainWindow as UMTK_MainWindow

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(Ui_MainWindow, self).__init__()

        self.desired_speed = 3.0
        self.X = []
        self.Y = []
        self.test_direction = 1
        self.theme_btn_red = "background-color: red"
        self.theme_btn_green = "background-color: green"
        self.UMTKSerial = UMTKSerial_t()

        self.ui = UMTK_MainWindow()
        self.ui.setupUi(self)

        self.ui.connectPort_but.pressed.connect(self.connect_serial_port)
        self.ui.disconnectPort_but.pressed.connect(self.disconnect_serial_port)
        
        self.ui.fwd_but.pressed.connect(self.increase_speed)
        self.ui.fwd_but.released.connect(self.stop_motor)
        self.ui.fwd_but.setAutoRepeat(True)
        self.ui.fwd_but.setAutoRepeatDelay(100)
        self.ui.bck_but.pressed.connect(self.decrease_speed)
        self.ui.bck_but.released.connect(self.stop_motor)
        self.ui.bck_but.setAutoRepeat(True)
        self.ui.bck_but.setAutoRepeatDelay(100)
        self.ui.tare_but.clicked.connect(self.tare)
        # self.speedDail.valueChanged.connect(self.update_speed)
        self.ui.start_but.clicked.connect(self.start_motor)
        self.ui.start_but_2.clicked.connect(self.start_motor)
        self.ui.stop_but.clicked.connect(self.stop_motor)
        self.ui.aux_but.clicked.connect(self.stop_motor)
        self.ui.aux_but.released.connect(self.stop_motor)
        # self.eStop.clicked.connect(self.estop_clicked)

        self.ui.setSpeed_but.clicked.connect(self.commit_speed)

        self.ui.calibration_but.pressed.connect(self.commit_calibrate)

        # self.ui.change_direction_but.clicked.connect(self.toggle_direction)

        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Force Displacement Graph")
        self.ax.set_xlabel("Displacement (mm)")
        self.ax.set_ylabel("Force (N)")
        self.sp, = self.ax.plot([],[],label='',ms=10,color='blue',marker='.',ls='')
        self.ui.graphDisplay.setLayout(QtWidgets.QVBoxLayout())
        self.ui.graphDisplay.layout().addWidget(self.canvas)

        self.initialize_serial_port()


    def initialize_serial_port(self):
        self.ui.portsDropdown.clear()
        self.ui.portsDropdown.addItems(self.UMTKSerial.init_serial())
        self.ui.textBrowser.setText(self.UMTKSerial.status_text)
    
    def rescan_serial_ports(self):
        self.ui.portsDropdown.clear()
        self.ui.portsDropdown.addItems(self.UMTKSerial.rescan_serial_ports())
        self.ui.textBrowser.setText(self.UMTKSerial.status_text)
    
    def connect_serial_port(self):
        picked_port = self.ui.portsDropdown.currentText()
        self.UMTKSerial.connect(picked_port)
        self.ui.textBrowser.setText(self.UMTKSerial.status_text)
        
    def disconnect_serial_port(self):
        self.UMTKSerial.disconnect()
        self.ui.textBrowser.setText(self.UMTKSerial.status_text)
        
    def read_serial(self):
        data = self.UMTKSerial.readData()
        self.ui.textBrowser.setText(self.UMTKSerial.status_text)
        self.process_serial_data(data)
        # Schedule Next Serial Read
        if (data):
            QtCore.QTimer().singleShot(25, self.read_serial)
        else:
            QtCore.QTimer().singleShot(150, self.read_serial)

    def process_serial_data(self, data):
        if (data):
            direction, position, load, cur_speed, set_speed, state, f_amps, b_amps, \
            bt_up, bt_down, bt_tare, bt_start, bt_aux, \
            v_in, v_mot, t_loop = data
            
            self.ui.displacementLCD.display(position)
            self.ui.forceLCD.display(load)
            self.ui.speedLCD.display(cur_speed)
            self.ui.umtkStateDisplay.setText(self.umtk_state_to_str(state))
            self.ui.maxForceLCD.display(load)
            self.ui.direction_indicator.setText("COMPRESSION" if direction == 1 else "TENSILE")

            self.ui.fwd_but.setStyleSheet(self.theme_btn_green) if bt_up else self.ui.fwd_but.setStyleSheet(self.theme_btn_red)
            self.ui.bck_but.setStyleSheet(self.theme_btn_green) if bt_down else self.ui.bck_but.setStyleSheet(self.theme_btn_red)
            self.ui.tare_but.setStyleSheet(self.theme_btn_green) if bt_tare else self.ui.tare_but.setStyleSheet(self.theme_btn_red)
            self.ui.start_but.setStyleSheet(self.theme_btn_green) if bt_start else self.ui.start_but.setStyleSheet(self.theme_btn_red)
            self.ui.aux_but.setStyleSheet(self.theme_btn_green) if bt_aux else self.ui.aux_but.setStyleSheet(self.theme_btn_red)

            self.X.append(position)
            self.Y.append(load)

            if len(self.X) > 1500:
                self.X = self.X[:1000]
                self.Y = self.Y[:1000]
            
            self.sp.set_data(self.X, self.Y)
            self.ax.set_xlim(min(min(self.X), -10),max(max(self.X), 10))
            self.ax.set_ylim(min(min(self.Y), -10), max(max(self.Y), 10))
            self.figure.canvas.draw()

            # Motor Effort, AMPs
            motorAmp = f_amps - b_amps
            #self.motorEffortProgressBar.setValue(int(motorAmp*1000))
            
            # Speed
            self.ui.motorSpeedProgessBar.setValue(int(cur_speed*100))

    def increase_speed(self):
        # Increase speed functionality
        self.UMTKSerial.write(b'U')

    def decrease_speed(self):
        # Decrease speed functionalityW
        self.UMTKSerial.write(b'D')

    def tare(self):
        # Tare functionality
        self.UMTKSerial.write(b'Tare\n')

    def commit_speed(self):
        try:
            self.UMTKSerial.write(f'V {str(float(self.setSpeed_inLine.text()))}\n'.encode())
        except:
            print("Error parsing set speed")
        # self.speedOutput.setText(str(self.desired_speed))

    def commit_calibrate(self):
        try:
            self.UMTKSerial.write(f'C {str(self.test_direction*float(self.calibration_inLine.text()))}\n'.encode())
        except:
            print("Error parsing calibration load")

    def update_speed(self, value):
        # Update speed functionality
        self.desired_speed = value/10

    def start_motor(self):
        # Start motor functionality
        self.UMTKSerial.write(b'Begin\n')

    def stop_motor(self):
        # Stop motor functionality
        self.UMTKSerial.write(b's')
        
    def toggle_direction(self):
        if self.direction_indicator.text() == "COMPRESSION":
            self.set_direction_up()
        else:
            self.set_direction_down()
            
        QtCore.QTimer().singleShot(100, self.tare)

    def set_direction_down(self):
        self.UMTKSerial.write(b'q')

    def set_direction_up(self):
        self.UMTKSerial.write(b'p')
        
    def estop_clicked(self):
        self.UMTKSerial.write(b's')

    def umtk_state_to_str(self, state):
        match state:
            case 0:
                return "RUNNING"
            case 1:
                return "IDLE"
            case 3:
                return "JOG UP"
            case 4:
                return "JOG DOWN"
            case 8:
                return "TARE"
            case _:
                return "UNKNOWN"

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt6())
    # apply_stylesheet(app, theme='light_amber.xml')

    # Load the QSS file
    file = QFile("modern_style.qss")
    if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())

    # Apply Fusion style
    # app.setStyle('Fusion')

    # # Customize colors for dark theme
    # palette = QtWidgets.QPalette()
    # palette.setColor(QtWidgets.QPalette.Window, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtWidgets.QPalette.WindowText, QtCore.Qt.white)
    # palette.setColor(QtWidgets.QPalette.Base, QtGui.QColor(25, 25, 25))
    # palette.setColor(QtWidgets.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtWidgets.QPalette.ToolTipBase, QtCore.Qt.white)
    # palette.setColor(QtWidgets.QPalette.ToolTipText, QtCore.Qt.white)
    # palette.setColor(QtWidgets.QPalette.Text, QtCore.Qt.white)
    # palette.setColor(QtWidgets.QPalette.Button, QtGui.QColor(53, 53, 53))
    # palette.setColor(QtWidgets.QPalette.ButtonText, QtCore.Qt.white)
    # palette.setColor(QtWidgets.QPalette.BrightText, QtCore.Qt.red)
    # app.setPalette(palette)

    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec())