from PyQt6 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from lib.UMTKSerial import UMTKSerial as UMTKSerial_t
import matplotlib.pyplot as plt 
import numpy as np
from datetime import datetime
from PyQt6.QtCore import QFile, QTextStream
from qt_material import apply_stylesheet
import csv
import os
import time

from lib.umtk_design import Ui_MainWindow as UMTK_MainWindow

class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self, theme):
        super(Ui_MainWindow, self).__init__()
        self.desired_speed = 3.0
        self.X = []
        self.Y = []
        self.test_direction = 1
        self.theme_btn_red = "background-color: red"
        self.theme_btn_green = "background-color: green"
        self.UMTKSerial = UMTKSerial_t()

        # Directory for logs
        self.log_dir = "UMTK_runs"
        os.makedirs(self.log_dir, exist_ok=True)

        # Start a new log file
        self.log_file = self.start_new_log()

        self.ui = UMTK_MainWindow()
        self.ui.setupUi(self)
        
        if theme == "Dark":
            plt.style.use('dark_background')
            dot_color = "yellow"
            self.ui.cat_2.setPixmap(QtGui.QPixmap("./img/cat_1k_dark.png"))
        else:
            dot_color = "blue"
            self.ui.cat_2.setPixmap(QtGui.QPixmap("./img/cat_1k.png"))

        self.ui.connectPort_but.pressed.connect(self.connect_serial_port)
        self.ui.disconnectPort_but.pressed.connect(self.disconnect_serial_port)
        
        self.ui.up_but.pressed.connect(self.increase_speed)
        self.ui.up_but.released.connect(self.stop_motor)
        self.ui.up_but.setAutoRepeat(True)
        self.ui.up_but.setAutoRepeatDelay(100)
        self.ui.down_but.pressed.connect(self.decrease_speed)
        self.ui.down_but.released.connect(self.stop_motor)
        self.ui.down_but.setAutoRepeat(True)
        self.ui.down_but.setAutoRepeatDelay(100)
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

        self.ui.changeDirection_but.clicked.connect(self.toggle_direction)

        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Force Displacement Graph")
        self.ax.set_xlabel("Displacement (mm)")
        self.ax.set_ylabel("Force (N)")
        self.sp, = self.ax.plot([],[],label='',ms=10,color=dot_color,marker='.',ls='')
        self.figure.tight_layout()
        self.ui.graphDisplay.setLayout(QtWidgets.QVBoxLayout())
        self.ui.graphDisplay.layout().addWidget(self.canvas)

        self.initialize_serial_port()

        # Set Serial Rate to 25Hz
        self.UMTKSerial.write(f'r20\n'.encode())

        # QtCore.QTimer().singleShot(10, self.connect_serial_port)
        QtCore.QTimer().singleShot(100, self.read_serial)

        self.rescan_serial_timer = QtCore.QTimer()
        self.rescan_serial_timer.timeout.connect(self.rescan_serial_ports)
        self.rescan_serial_timer.start(10000)

    def start_new_log(self):
        """Create a new log file with a unique timestamped name."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_file_path = os.path.join(self.log_dir, f"UMTK_run_{timestamp}.csv")
        log_file = open(log_file_path, "w", newline='')
        csv_writer = csv.writer(log_file)
        csv_writer.writerow(["Log Timestamp", "UMTK Time Counter", "Direction", "Position", "Load", "Current Speed", "Set Speed", "State", "F_AMPS", "B_AMPS", "BT_Up", "BT_Down", "BT_Tare", "BT_Start", "BT_Aux", "V_Mot", "V_In", "T_Loop"])
        return log_file

    def log_data(self, data):
        """Log serial data to the CSV file."""
        if self.log_file and data:
            csv_writer = csv.writer(self.log_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            csv_writer.writerow([timestamp, *data])

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
            # Log the data continuously
            self.log_data(data)
            QtCore.QTimer().singleShot(25, self.read_serial)
        else:
            QtCore.QTimer().singleShot(150, self.read_serial)

    def process_serial_data(self, data):
        if (data):
            millis, direction, position, load, cur_speed, set_speed, state, f_amps, b_amps, \
            bt_up, bt_down, bt_tare, bt_start, bt_aux, \
            v_mot, v_in, t_loop = data
            
            self.ui.displacementLCD.display(position)
            self.ui.forceLCD.display(load)
            self.ui.speedLCD.display(cur_speed)
            self.ui.textBrowser_2.setHtml(self.umtk_state_to_str(state))
            self.ui.maxForceLCD.display(max(self.Y) if self.Y else load)
            self.ui.changeDirection_inLine.setText("COMPRESSION" if direction == 1 else "TENSILE")

            self.ui.down_but.setStyleSheet(self.theme_btn_green) if bt_up else self.ui.down_but.setStyleSheet(self.theme_btn_red)
            self.ui.up_but.setStyleSheet(self.theme_btn_green) if bt_down else self.ui.up_but.setStyleSheet(self.theme_btn_red)
            self.ui.tare_but.setStyleSheet(self.theme_btn_green) if bt_tare else self.ui.tare_but.setStyleSheet(self.theme_btn_red)
            self.ui.start_but.setStyleSheet(self.theme_btn_green) if bt_start else self.ui.start_but.setStyleSheet(self.theme_btn_red)
            self.ui.aux_but.setStyleSheet(self.theme_btn_green) if bt_aux else self.ui.aux_but.setStyleSheet(self.theme_btn_red)
            if (v_mot < 3):
                self.ui.eStop_display.setStyleSheet(self.theme_btn_red)

            # if state is TARE, clear graph
            if state == 8:
                if self.log_file:
                    self.log_file.close()
                    self.log_file = self.start_new_log()
                self.X = []
                self.Y = []
            else:
                self.X.append(position)
                self.Y.append(load)

                if len(self.X) > 1500:
                    self.X = self.X[:1000]
                    self.Y = self.Y[:1000]
                
                if (direction == 1):
                    self.sp.set_data(self.X, self.Y)
                else:
                    self.sp.set_data(self.X, self.Y)
                self.ax.set_xlim(min(min(self.X), -10),max(max(self.X), 10))
                self.ax.set_ylim(min(min(self.Y), -10), max(max(self.Y), 10))
            self.figure.canvas.draw()
            
            # Motor Power
            motor_amps= (f_amps + b_amps)
            self.ui.motorCurrent_display.display("{:1.2f}".format(motor_amps))
            self.ui.motorCurrent_display.setStyleSheet("") if (motor_amps < 4) else self.ui.motorCurrent_display.setStyleSheet(self.theme_btn_red)


    def increase_speed(self):
        # Increase speed functionality
        self.UMTKSerial.write(b'U')

    def decrease_speed(self):
        # Decrease speed functionalityW
        self.UMTKSerial.write(b'D')

    def tare(self):
        """Stop current logging and start a new log."""
        # Tare functionality
        self.UMTKSerial.write(b'Tare\n')
        if self.log_file:
            self.log_file.close()
        self.log_file = self.start_new_log()

    def commit_speed(self):
        try:
            speed = str(float(self.ui.setSpeed_inLine.text()))
            self.UMTKSerial.write(f'V {speed}\n'.encode())
            print(f"Commanded Set Speed: {speed}")
        except:
            print("Error parsing set speed")
        # self.speedOutput.setText(str(self.desired_speed))

    def commit_calibrate(self):
        try:
            self.UMTKSerial.write(f'C {str(self.test_direction*float(self.ui.calibration_inLine.text()))}\n'.encode())
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
        if self.ui.changeDirection_inLine.text() == "COMPRESSION":
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
        state_name = ""
        match state:
            case 0:
                state_name = "RUNNING"
            case 1:
                state_name = "IDLE"
            case 3:
                state_name =  "JOG UP"
            case 4:
                state_name =  "JOG DOWN"
            case 8:
                state_name =  "TARE"
            case _:
                state_name =  "UNKNOWN"
            
        return (f"<p align=\"center\" style=\" font-family:\'.AppleSystemUIFont\'; font-size:20pt; font-weight:600; font-style:normal;\">{state_name}</p>")
    
    def closeEvent(self, event):
        """Close the log file when the application is closed."""
        if self.log_file:
            self.log_file.close()
        event.accept()

if __name__ == "__main__":
    import sys

    theme = "Dark"

    app = QtWidgets.QApplication(sys.argv)
    
    MainWindow = Ui_MainWindow(theme)

    # Load the QSS file
    if theme == "Dark":
        file = QFile("style/Dark.qss")
    else:
        file = QFile("style/modern_style.qss")
    if file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
        MainWindow.setStyleSheet(stream.readAll())

    MainWindow.show()
    sys.exit(app.exec())