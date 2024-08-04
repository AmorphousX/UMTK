# UPDATED WITH MACOS PORTS AND IGNORED LAMBDA FUNCTIONS FOR EASY EDITIABILITY
from PyQt6 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import serial
import serial.tools.list_ports
import random
import serial.tools.list_ports

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1440, 800)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 650, 1421, 111))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.up_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.up_but.setObjectName("up_but")
        self.verticalLayout_3.addWidget(self.up_but)
        self.down_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.down_but.setObjectName("down_but")
        self.verticalLayout_3.addWidget(self.down_but)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        spacerItem = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tare_but_2 = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.tare_but_2.setObjectName("tare_but_2")
        self.verticalLayout_4.addWidget(self.tare_but_2)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        spacerItem1 = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.speedDail = QtWidgets.QDial(parent=self.horizontalLayoutWidget)
        self.speedDail.setObjectName("speedDail")
        self.verticalLayout_5.addWidget(self.speedDail)
        self.speedOutput = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.speedOutput.setObjectName("speedOutput")
        self.verticalLayout_5.addWidget(self.speedOutput, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        spacerItem2 = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.setSpeed_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.setSpeed_but.setObjectName("setSpeed_but")
        self.verticalLayout.addWidget(self.setSpeed_but)
        self.setSpeed_Label = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.setSpeed_Label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.setSpeed_Label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setSpeed_Label.setObjectName("setSpeed_Label")
        self.verticalLayout.addWidget(self.setSpeed_Label)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem3 = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.start_but_2 = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.start_but_2.setObjectName("start_but_2")
        self.verticalLayout_6.addWidget(self.start_but_2)
        self.stop_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.stop_but.setObjectName("stop_but")
        self.verticalLayout_6.addWidget(self.stop_but)
        self.horizontalLayout.addLayout(self.verticalLayout_6)
        self.graphDisplay = QtWidgets.QWidget(parent=self.centralwidget)
        self.graphDisplay.setGeometry(QtCore.QRect(10, 50, 1061, 591))
        self.graphDisplay.setObjectName("graphDisplay")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 0, 1421, 51))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.banner = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.banner.setContentsMargins(0, 0, 0, 0)
        self.banner.setObjectName("banner")
        self.bannerName = QtWidgets.QLabel(parent=self.horizontalLayoutWidget_2)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.bannerName.setFont(font)
        self.bannerName.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.bannerName.setAutoFillBackground(False)
        self.bannerName.setStyleSheet("")
        self.bannerName.setObjectName("bannerName")
        self.banner.addWidget(self.bannerName, 0, QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(1070, 50, 361, 401))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.display = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.display.setContentsMargins(0, 0, 0, 0)
        self.display.setObjectName("display")
        self.displacement = QtWidgets.QLabel(parent=self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.displacement.setFont(font)
        self.displacement.setObjectName("displacement")
        self.display.addWidget(self.displacement)
        self.displacementLCD = QtWidgets.QLCDNumber(parent=self.verticalLayoutWidget_2)
        self.displacementLCD.setObjectName("displacementLCD")
        self.display.addWidget(self.displacementLCD)
        self.force = QtWidgets.QLabel(parent=self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.force.setFont(font)
        self.force.setObjectName("force")
        self.display.addWidget(self.force)
        self.forceLCD = QtWidgets.QLCDNumber(parent=self.verticalLayoutWidget_2)
        self.forceLCD.setObjectName("forceLCD")
        self.display.addWidget(self.forceLCD)
        self.speed = QtWidgets.QLabel(parent=self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.speed.setFont(font)
        self.speed.setObjectName("speed")
        self.display.addWidget(self.speed)
        self.speedLCD = QtWidgets.QLCDNumber(parent=self.verticalLayoutWidget_2)
        self.speedLCD.setObjectName("speedLCD")
        self.display.addWidget(self.speedLCD)
        self.umtkSate = QtWidgets.QLabel(parent=self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.umtkSate.setFont(font)
        self.umtkSate.setObjectName("umtkSate")
        self.display.addWidget(self.umtkSate)
        self.umtkStateLCD = QtWidgets.QLCDNumber(parent=self.verticalLayoutWidget_2)
        self.umtkStateLCD.setObjectName("umtkStateLCD")
        self.display.addWidget(self.umtkStateLCD)
        self.maxForce = QtWidgets.QLabel(parent=self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.maxForce.setFont(font)
        self.maxForce.setObjectName("maxForce")
        self.display.addWidget(self.maxForce)
        self.maxForceLCD = QtWidgets.QLCDNumber(parent=self.verticalLayoutWidget_2)
        self.maxForceLCD.setObjectName("maxForceLCD")
        self.display.addWidget(self.maxForceLCD)
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(1070, 450, 361, 121))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.motorstall_eStop = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.motorstall_eStop.setContentsMargins(0, 0, 0, 0)
        self.motorstall_eStop.setObjectName("motorstall_eStop")
        self.motorstall = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.motorstall.setFont(font)
        self.motorstall.setObjectName("motorstall")
        self.motorstall_eStop.addWidget(self.motorstall)
        self.motorstallProgressBar = QtWidgets.QProgressBar(parent=self.verticalLayoutWidget)
        self.motorstallProgressBar.setProperty("value", 24)
        self.motorstallProgressBar.setObjectName("motorstallProgressBar")
        self.motorstall_eStop.addWidget(self.motorstallProgressBar)
        self.estop = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.estop.setFont(font)
        self.estop.setObjectName("estop")
        self.motorstall_eStop.addWidget(self.estop)
        self.estopProgressBar = QtWidgets.QProgressBar(parent=self.verticalLayoutWidget)
        self.estopProgressBar.setProperty("value", 24)
        self.estopProgressBar.setObjectName("estopProgressBar")
        self.motorstall_eStop.addWidget(self.estopProgressBar)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1440, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Sample Graph")
        self.ax.set_xlabel("X Axis")
        self.ax.set_ylabel("Y Axis")
        self.graphDisplay.setLayout(QtWidgets.QVBoxLayout())
        self.graphDisplay.layout().addWidget(self.canvas)

        self.up_but.clicked.connect(self.increase_speed)
        self.down_but.clicked.connect(self.decrease_speed)
        self.tare_but_2.clicked.connect(self.tare)
        self.speedDail.valueChanged.connect(self.update_speed)
        self.start_but_2.clicked.connect(self.start_motor)
        self.stop_but.clicked.connect(self.stop_motor)
        # self.eStop.clicked.connect(self.estop_clicked)

        self.serialPort = self.initialize_serial_port()

        self.serialTimer = QtCore.QTimer()
        self.serialTimer.timeout.connect(self.read_serial)
        self.serialTimer.start(100)  # Read serial every 100ms

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.up_but.setText(_translate("MainWindow", "Up"))
        self.down_but.setText(_translate("MainWindow", "Down"))
        self.tare_but_2.setText(_translate("MainWindow", "Tare"))
        self.speedOutput.setText(_translate("MainWindow", "Speed Output"))
        self.start_but_2.setText(_translate("MainWindow", "Start"))
        self.stop_but.setText(_translate("MainWindow", "Stop"))
        self.bannerName.setText(_translate("MainWindow", "Test Stand GUI"))
        self.displacement.setText(_translate("MainWindow", "Displacement"))
        self.force.setText(_translate("MainWindow", "Force"))
        self.speed.setText(_translate("MainWindow", "Speed"))
        self.setSpeed_but.setText(_translate("MainWindow", "Set Speed"))
        self.setSpeed_Label.setText(_translate("MainWindow", "Set Speed Label"))
        self.umtkSate.setText(_translate("MainWindow", "UMTK State"))
        self.maxForce.setText(_translate("MainWindow", "Max Force"))
        self.motorstall.setText(_translate("MainWindow", "Motor Stall"))
        self.estop.setText(_translate("MainWindow", "E-Stop"))

    def initialize_serial_port(self):
        # List all available serial ports
        # ports = serial.tools.list_ports.list_ports()
        
        # if ports:
            # Use the first available serial port
        port_name = "COM7"
        print(f"Using serial port: {port_name}")
        try:
            return serial.Serial(port_name, 250000, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return None
        # else:
        #     # No serial ports found, use default mode
        #     print("No serial ports found. Using default mode.")
        #     return None

    def read_serial(self):
        if self.serialPort and self.serialPort.is_open:
            try:
                line = self.serialPort.readline()
                # print(line)
                print(".",end="", flush=True)
                data = line.decode().strip()
                if data:
                    # print(f"Received: {data}")
                    self.process_serial_data(data)
            except serial.SerialException as e:
                print(f"Error reading serial port: {e}")

    def process_serial_data(self, data):
        try:
            values = list(map(float, data.split('\t')))
            if len(values) >= 6:
                position, load, cur_speed, set_speed, state, f_amps, b_amps, bt_up, \
                    bt_down, bt_tare, bt_aux, t_loop = values
                self.displacementLCD.display(position)
                self.forceLCD.display(load)
                self.speedLCD.display(cur_speed)
                self.umtkStateLCD.display(state)
                self.maxForceLCD.display(load)
                self.motorstallProgressBar.setValue(int(f_amps - b_amps))
                self.estopProgressBar.setValue(int(estop))
        except ValueError as e:
            print(f"Error processing serial data: {e}")

    def increase_speed(self):
        # Increase speed functionality
        self.serialPort.write(b'U')

    def decrease_speed(self):
        # Decrease speed functionality
        self.serialPort.write(b'D')

    def tare(self):
        # Tare functionality
        self.serialPort.write(b'Tare')

    def update_speed(self, value):
        # Update speed functionality
        self.serialPort.write(f'V {value}\n'.encode())
        self.speedOutput.setText(str(value))

    def start_motor(self):
        # Start motor functionality
        self.serialPort.write(b'Begin')

    def stop_motor(self):
        # Stop motor functionality
        self.serialPort.write(b's')
        
    def estop_clicked(self):
        self.serialPort.write(b's')

    def generate_random_data_for_demo(self):
        # Generate and display random data for demo purposes
        displacement = random.uniform(0, 100)
        force = random.uniform(0, 500)
        speed = random.uniform(0, 200)
        umtk_state = random.randint(0, 5)
        max_force = random.uniform(0, 500)
        motor_stall = random.randint(0, 100)
        
        self.displacementLCD.display(displacement)
        self.forceLCD.display(force)
        self.speedLCD.display(speed)
        self.umtkStateLCD.display(umtk_state)
        self.maxForceLCD.display(max_force)
        self.motorstallProgressBar.setValue(motor_stall)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())