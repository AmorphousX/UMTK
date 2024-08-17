# UPDATED WITH MACOS PORTS AND IGNORED LAMBDA FUNCTIONS FOR EASY EDITIABILITY
from PyQt6 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt 
import numpy as np
import serial
import serial.tools.list_ports
import random
import serial.tools.list_ports
import copy
import logging

class Ui_MainWindow(object):
    desired_speed = 3.0
    serial_port_holder = dict(status = None, name = None, handle = None)
    serialPort = None
    X = []
    Y = []

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1440, 785)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 640, 1051, 141))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        ##########
        self.verticalLayout_7.setObjectName("verticalLayout_7")

        self.portsDropdown = QtWidgets.QComboBox(parent=self.horizontalLayoutWidget)
        self.portsDropdown.setObjectName("portsDropdown")
        self.verticalLayout_7.addWidget(self.portsDropdown)

        self.serialStatus = QtWidgets.QTextBrowser(parent=self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.serialStatus.sizePolicy().hasHeightForWidth())
        self.serialStatus.setSizePolicy(sizePolicy)
        self.serialStatus.setMaximumSize(QtCore.QSize(330, 25))
        self.serialStatus.setObjectName("serialStatus")
        self.verticalLayout_7.addWidget(self.serialStatus)
        self.connectPort_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.connectPort_but.setObjectName("connectPort_but")
        self.verticalLayout_7.addWidget(self.connectPort_but)
        self.disconnectPort_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.disconnectPort_but.setObjectName("disconnectPort_but")
        self.verticalLayout_7.addWidget(self.disconnectPort_but)

        self.horizontalLayout.addLayout(self.verticalLayout_7)
        spacerItem = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.calibration = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.calibration.setMaximumSize(QtCore.QSize(16777215, 30))
        self.calibration.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.calibration.setObjectName("calibration")
        self.verticalLayout.addWidget(self.calibration)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.calibration_inLine = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calibration_inLine.sizePolicy().hasHeightForWidth())
        self.calibration_inLine.setSizePolicy(sizePolicy)
        self.calibration_inLine.setMaximumSize(QtCore.QSize(320, 16777215))
        self.calibration_inLine.setInputMask("")
        self.calibration_inLine.setText("")
        self.calibration_inLine.setObjectName("calibration_inLine")
        self.horizontalLayout_2.addWidget(self.calibration_inLine)
        self.newtons = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.newtons.setMaximumSize(QtCore.QSize(35, 16777215))
        self.newtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.newtons.setObjectName("newtons")
        self.horizontalLayout_2.addWidget(self.newtons)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.calibration_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.calibration_but.setObjectName("calibration_but")
        self.verticalLayout.addWidget(self.calibration_but)
        self.horizontalLayout.addLayout(self.verticalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        self.label = QtWidgets.QLabel(parent=self.horizontalLayoutWidget)
        self.label.setMaximumSize(QtCore.QSize(16777215, 30))
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.setSpeed_inLine = QtWidgets.QLineEdit(parent=self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.setSpeed_inLine.sizePolicy().hasHeightForWidth())
        self.setSpeed_inLine.setSizePolicy(sizePolicy)
        self.setSpeed_inLine.setMaximumSize(QtCore.QSize(329, 16777215))
        self.setSpeed_inLine.setObjectName("setSpeed_inLine")
        self.verticalLayout_5.addWidget(self.setSpeed_inLine)
        self.setSpeed_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.setSpeed_but.setObjectName("setSpeed_but")

        self.verticalLayout_5.addWidget(self.setSpeed_but)
        self.horizontalLayout.addLayout(self.verticalLayout_5)
        spacerItem2 = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.start2_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget)
        self.start2_but.setObjectName("start2_but")
        self.verticalLayout_6.addWidget(self.start2_but)
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
        self.umtkStateDisplay = QtWidgets.QLineEdit(parent=self.verticalLayoutWidget_2)
        self.umtkStateDisplay.setObjectName("umtkStateDisplay")
        self.umtkStateDisplay.setEnabled(False)
        self.display.addWidget(self.umtkStateDisplay)
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
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(1070, 450, 361, 251))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.motorstall_eStop = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.motorstall_eStop.setContentsMargins(0, 0, 0, 0)
        self.motorstall_eStop.setObjectName("motorstall_eStop")

        self.motorEffort = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.motorEffort.setFont(font)
        self.motorEffort.setObjectName("motorEffort")
        self.motorstall_eStop.addWidget(self.motorEffort)
        self.motorEffortProgressBar = QtWidgets.QProgressBar(parent=self.verticalLayoutWidget)
        self.motorEffortProgressBar.setProperty("value", 5)
        self.motorEffortProgressBar.setMinimum(-10000)
        self.motorEffortProgressBar.setMaximum(10000)
        self.motorEffortProgressBar.setObjectName("motorEffortProgressBar")
        self.motorstall_eStop.addWidget(self.motorEffortProgressBar)
        self.motorSpeed = QtWidgets.QLabel(parent=self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.motorSpeed.setFont(font)
        self.motorSpeed.setObjectName("motorSpeed")
        self.motorstall_eStop.addWidget(self.motorSpeed)
        self.motorSpeedProgessBar = QtWidgets.QProgressBar(parent=self.verticalLayoutWidget)
        self.motorSpeedProgessBar.setProperty("value", 5)
        self.motorSpeedProgessBar.setMinimum(-1000)
        self.motorSpeedProgessBar.setMaximum(1000)
        self.motorSpeedProgessBar.setObjectName("motorSpeedProgessBar")
        self.motorstall_eStop.addWidget(self.motorSpeedProgessBar)
        
        self.eStop_but = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.eStop_but.setObjectName("eStop_but")
        self.motorstall_eStop.addWidget(self.eStop_but)
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(parent=self.centralwidget)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(1070, 700, 361, 81))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.buttonStatus = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.buttonStatus.setContentsMargins(0, 0, 0, 0)
        self.buttonStatus.setObjectName("buttonStatus")
        self.up_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.up_but.setEnabled(True)
        self.up_but.setMaximumSize(QtCore.QSize(60, 70))

        font = QtGui.QFont()

        font.setPointSize(9)
        self.up_but.setFont(font)
        self.up_but.setMouseTracking(False)
        self.up_but.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhNone)
        self.up_but.setObjectName("up_but")
        self.buttonStatus.addWidget(self.up_but)
        self.down_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.down_but.setMaximumSize(QtCore.QSize(60, 70))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.down_but.setFont(font)
        self.down_but.setObjectName("down_but")
        self.buttonStatus.addWidget(self.down_but)
        self.tare_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.tare_but.setMaximumSize(QtCore.QSize(60, 70))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.tare_but.setFont(font)
        self.tare_but.setObjectName("tare_but")
        self.buttonStatus.addWidget(self.tare_but)
        self.start_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.start_but.setMaximumSize(QtCore.QSize(60, 70))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.start_but.setFont(font)
        self.start_but.setObjectName("start_but")
        self.buttonStatus.addWidget(self.start_but)
        self.aux_but = QtWidgets.QPushButton(parent=self.horizontalLayoutWidget_3)
        self.aux_but.setMaximumSize(QtCore.QSize(60, 70))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.aux_but.setFont(font)
        self.aux_but.setObjectName("aux_but")
        self.buttonStatus.addWidget(self.aux_but)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1440, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        # self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        # self.statusbar.setObjectName("statusbar")
        # MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Force Displacement Graph")
        self.ax.set_xlabel("Displacement (mm)")
        self.ax.set_ylabel("Force (N)")
        self.sp, = self.ax.plot([],[],label='',ms=10,color='blue',marker='.',ls='')
        self.graphDisplay.setLayout(QtWidgets.QVBoxLayout())
        self.graphDisplay.layout().addWidget(self.canvas)


        self.connectPort_but.pressed.connect(self.connect_serial_port)
        self.disconnectPort_but.pressed.connect(self.disconnect_serial_port)

        self.up_but.pressed.connect(self.increase_speed)
        self.up_but.released.connect(self.stop_motor)
        self.up_but.setAutoRepeat(True)
        self.up_but.setAutoRepeatDelay(100)
        self.down_but.pressed.connect(self.decrease_speed)
        self.down_but.released.connect(self.stop_motor)
        self.down_but.setAutoRepeat(True)
        self.down_but.setAutoRepeatDelay(100)
        self.tare_but.clicked.connect(self.tare)
        # self.speedDail.valueChanged.connect(self.update_speed)
        self.start_but.clicked.connect(self.start_motor)
        self.start2_but.clicked.connect(self.start_motor)
        self.stop_but.clicked.connect(self.stop_motor)
        self.aux_but.clicked.connect(self.stop_motor)
        self.aux_but.released.connect(self.stop_motor)
        # self.eStop.clicked.connect(self.estop_clicked)

        self.setSpeed_but.clicked.connect(self.commit_speed)

        self.calibration_but.pressed.connect(self.commit_calibrate)

        self.initialize_serial_port()

        
        QtCore.QTimer().singleShot(10, self.connect_serial_port)
        QtCore.QTimer().singleShot(100, self.read_serial)

        self.screen_rescale_timer = QtCore.QTimer()
        self.screen_rescale_timer.timeout.connect(self.scale_ui_to_screen)
        self.screen_rescale_timer.start(1000)
        
        # Auto Connect Serial Port
        # self.serialTimer.start(100)  # Read serial continuously

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.connectPort_but.setText(_translate("MainWindow", "Connect"))
        self.disconnectPort_but.setText(_translate("MainWindow", "Disconnect"))
        self.calibration.setText(_translate("MainWindow", "Calibration"))
        self.newtons.setText(_translate("MainWindow", "N"))
        self.calibration_but.setText(_translate("MainWindow", "Calibrate"))
        self.label.setText(_translate("MainWindow", "Set Speed"))
        self.setSpeed_but.setText(_translate("MainWindow", "Set Speed"))

        self.start2_but.setText(_translate("MainWindow", "Start"))
        self.start_but.setText(_translate("MainWindow", "Start"))
        self.stop_but.setText(_translate("MainWindow", "Stop"))
        self.bannerName.setText(_translate("MainWindow", "Test Stand GUI"))
        self.displacement.setText(_translate("MainWindow", "Displacement"))
        self.force.setText(_translate("MainWindow", "Force"))
        self.speed.setText(_translate("MainWindow", "Speed"))
        self.umtkSate.setText(_translate("MainWindow", "UMTK State"))
        self.maxForce.setText(_translate("MainWindow", "Max Force"))
        self.motorEffort.setText(_translate("MainWindow", "Motor Effort"))
        self.motorSpeed.setText(_translate("MainWindow", "Motor Speed"))

        self.eStop_but.setText(_translate("MainWindow", "eStop"))
        self.up_but.setText(_translate("MainWindow", "JOG\nUP"))
        self.down_but.setText(_translate("MainWindow", "JOG\nDOWN"))
        self.tare_but.setText(_translate("MainWindow", "TARE"))
        self.start_but.setText(_translate("MainWindow", "START"))
        self.aux_but.setText(_translate("MainWindow", "AUX"))

    def scale_ui_to_screen(self):
        screen = QtWidgets.QApplication.primaryScreen()
        screen_size = screen.size()
        screen_width = screen_size.width()
        screen_height = screen_size.height()

        # Resize the window to a percentage of the screen size
        MainWindow.resize(int(screen_width * 0.8), int(screen_height * 0.8))
                          

    def initialize_serial_port(self):
        # List all available serial ports
        ports = serial.tools.list_ports.comports()
        self.portsDropdown.clear()
        
        if ports:
            for this_port in ports:
                self.portsDropdown.addItem(this_port.device)
        else:
            self.portsDropdown.addItem("NO PORTS AVAILABLE")
    
    def connect_serial_port(self):
        picked_port = self.portsDropdown.currentText()
        if picked_port == "NO PORTS AVAILABLE" or picked_port is None:
            return
        print(f"Connecting serial port: {picked_port}")
        self.serialStatus.setText(f"{picked_port} Connecting......")

        try:
            this_port = serial.Serial(picked_port, 250000, timeout=1)
            self.serial_port_holder = dict (
                handle = this_port,
                status = True,
                name = picked_port
                )
            self.serialPort = this_port
            return
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return None
        
    def disconnect_serial_port(self):
        if self.serial_port_holder["status"]:
            print(f"Disconnecting serial port: {self.serial_port_holder['name']}")
            self.serial_port_holder["handle"].close()
            self.serial_port_holder["status"] = False
            logging.info("Port {} disconnected".format(self.serial_port_holder["name"]))
        else:
            logging.debug("Port not connected")

        return

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
                self.serialStatus.setText("Connected: {}".format(self.serial_port_holder["name"]))
            except serial.SerialException as e:
                print(f"Error reading serial port: {e}")
                self.serialStatus.setText("ERROR: {}".format(self.serial_port_holder["name"]))
            finally:
                # Schedule Next Serial Read
                QtCore.QTimer().singleShot(10, self.read_serial)
        else:
            self.serialStatus.setText("Disonnected")


    def process_serial_data(self, data):
        if ("== TARE ==" in data):
            # Tare
            self.X = []
            self.Y = []
            print("T", end="")
        elif ("DIRECTION" in data):
            # Header
            print("H", end="")
        else:
            try:
            # Data
                values = list(data.split('\t'))
                if len(values) >= 14:
                    i_direction, i_position, i_load, i_cur_speed, i_set_speed, i_state, \
                    i_f_amps, i_b_amps, i_bt_up, i_bt_down, i_bt_tare, i_bt_start,\
                    i_bt_aux, i_v_in, i_v_mot, i_t_loop = values
                    
                    diection = int(i_direction)
                    position = float(i_position)
                    load = float(i_load)
                    cur_speed = float(i_cur_speed)
                    set_speed = float(i_set_speed)
                    state = int(i_state)
                    f_amps = float(i_f_amps)
                    b_amps = float(i_b_amps)
                    bt_up = True if i_bt_up == "1" else False
                    bt_down = True if i_bt_down == "1" else False
                    bt_tare = True if i_bt_tare == "1" else False
                    bt_start = True if i_bt_start == "1" else False
                    bt_aux = True if i_bt_aux == "1" else False
                    v_in = float(i_v_in)
                    v_mot = float(i_v_mot)
                    t_loop = int(i_t_loop)

                    self.displacementLCD.display(position)
                    self.forceLCD.display(load)
                    self.speedLCD.display(cur_speed)
                    self.umtkStateDisplay.setText(self.umtk_state_to_str(state))
                    self.maxForceLCD.display(load)

                    self.up_but.setStyleSheet("background-color: green") if bt_up else self.up_but.setStyleSheet("background-color: red")
                    self.down_but.setStyleSheet("background-color: green") if bt_down else self.down_but.setStyleSheet("background-color: red")
                    self.tare_but.setStyleSheet("background-color: green") if bt_tare else self.tare_but.setStyleSheet("background-color: red")
                    self.start_but.setStyleSheet("background-color: green") if bt_start else self.start_but.setStyleSheet("background-color: red")
                    self.aux_but.setStyleSheet("background-color: green") if bt_aux else self.aux_but.setStyleSheet("background-color: red")
                    
                    # print(values)
                        
                    # self.motorstall_eStop.setValue(int(f_amps - b_amps))
                    # self.estopProgressBar.setValue(int(v_mot))

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
                    self.motorEffortProgressBar.setValue(int(motorAmp*1000))
                    
                    # Speed
                    self.motorSpeedProgessBar.setValue(int(cur_speed*100))

            except ValueError as e:
                print(f"Error processing serial data: {e}")
                print(data)

    def increase_speed(self):
        # Increase speed functionality
        self.serialPort.write(b'U')

    def decrease_speed(self):
        # Decrease speed functionality
        self.serialPort.write(b'D')

    def tare(self):
        # Tare functionality
        self.serialPort.write(b'Tare\n')

    def commit_speed(self):
        try:
            self.serialPort.write(f'V {str(float(self.setSpeed_inLine.text()))}\n'.encode())
        except:
            print("Error parsing set speed")
        # self.speedOutput.setText(str(self.desired_speed))

    def commit_calibrate(self):
        try:
            self.serialPort.write(f'C {str(float(self.calibration_inLine.text()))}\n'.encode())
        except:
            print("Error parsing calibration load")

    def update_speed(self, value):
        # Update speed functionality
        self.desired_speed = value/10

    def start_motor(self):
        # Start motor functionality
        self.serialPort.write(b'Begin\n')

    def stop_motor(self):
        # Stop motor functionality
        self.serialPort.write(b's')
        
    def set_direction_down(self):
        self.serialPort.write(b'q')

    def set_direction_up(self):
        self.serialPort.write(b'p')
        
    def estop_clicked(self):
        self.serialPort.write(b's')

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
            case _:
                return "UNKNOWN"



    # def generate_random_data_for_demo(self):
    #     # Generate and display random data for demo purposes
    #     displacement = random.uniform(0, 100)
    #     force = random.uniform(0, 500)
    #     speed = random.uniform(0, 200)
    #     umtk_state = random.randint(0, 5)
    #     max_force = random.uniform(0, 500)
    #     motor_stall = random.randint(0, 100)
        
    #     self.displacementLCD.display(displacement)
    #     self.forceLCD.display(force)
    #     self.speedLCD.display(speed)
    #     self.umtkStateDisplay.display(umtk_state)
    #     self.maxForceLCD.display(max_force)
    #     self.motorstall_eStop.setValue(motor_stall)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())