"""
Chatgpu made layout dynamic
"""

try:
        from PyQt6 import QtCore, QtGui, QtWidgets
except ImportError:  # Fallback to PySide6 if PyQt6 is unavailable
        from PySide6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
        def setupUi(self, MainWindow):
                MainWindow.setObjectName("MainWindow")
                MainWindow.resize(1366, 768)
                MainWindow.setMinimumSize(QtCore.QSize(900, 600))

                self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
                self.centralwidget.setObjectName("centralwidget")
                MainWindow.setCentralWidget(self.centralwidget)

                # Top-level layout
                self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
                self.mainLayout.setContentsMargins(8, 8, 8, 8)
                self.mainLayout.setSpacing(8)

                # ----- Top banner row -----
                self.topBanner = QtWidgets.QHBoxLayout()
                self.topBanner.setContentsMargins(0, 0, 0, 0)
                self.topBanner.setSpacing(8)

                self.topBanner.addItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))

                self.bannerName = QtWidgets.QLabel(parent=self.centralwidget)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
                self.bannerName.setSizePolicy(sizePolicy)
                font = QtGui.QFont()
                font.setPointSize(36)
                font.setBold(True)
                self.bannerName.setFont(font)
                self.bannerName.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.bannerName.setObjectName("bannerName")
                self.topBanner.addWidget(self.bannerName, 10)

                self.cat_2 = QtWidgets.QLabel(parent=self.centralwidget)
                self.cat_2.setEnabled(True)
                sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
                self.cat_2.setSizePolicy(sizePolicy)
                self.cat_2.setMinimumSize(QtCore.QSize(70, 70))
                self.cat_2.setMaximumSize(QtCore.QSize(100, 100))
                self.cat_2.setText("")
                self.cat_2.setPixmap(QtGui.QPixmap("img/cat_1k.png"))
                self.cat_2.setScaledContents(True)
                self.cat_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.cat_2.setObjectName("cat_2")
                self.topBanner.addWidget(self.cat_2)

                self.topBanner.addItem(QtWidgets.QSpacerItem(5, 10, QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Minimum))

                self.mainLayout.addLayout(self.topBanner)

                # ----- Content row (graph left, metrics right) -----
                self.contentRow = QtWidgets.QHBoxLayout()
                self.contentRow.setContentsMargins(0, 0, 0, 0)
                self.contentRow.setSpacing(8)

                # Left column with graph and bottom controls
                self.leftColumn = QtWidgets.QVBoxLayout()
                self.leftColumn.setSpacing(8)

                # Graph display placeholder (main.py adds a layout+canvas here)
                self.graphDisplay = QtWidgets.QWidget(parent=self.centralwidget)
                self.graphDisplay.setObjectName("graphDisplay")
                self.graphDisplay.setSizePolicy(
                        QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
                )
                self.leftColumn.addWidget(self.graphDisplay, 10)

                # Bottom controls area (single row, multiple vertical groups)
                self.controlsRow = QtWidgets.QHBoxLayout()
                self.controlsRow.setSpacing(8)

                # Serial/port controls
                self.serialCol = QtWidgets.QVBoxLayout()
                self.serialCol.setSpacing(4)
                self.portsDropdown = QtWidgets.QComboBox(parent=self.centralwidget)
                self.portsDropdown.setObjectName("portsDropdown")
                self.serialCol.addWidget(self.portsDropdown)

                self.textBrowser = QtWidgets.QTextBrowser(parent=self.centralwidget)
                self.textBrowser.setObjectName("textBrowser")
                self.textBrowser.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
                self.textBrowser.setFixedHeight(40)
                self.serialCol.addWidget(self.textBrowser)

                btnRow1 = QtWidgets.QHBoxLayout()
                self.connectPort_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.connectPort_but.setObjectName("connectPort_but")
                btnRow1.addWidget(self.connectPort_but)
                self.disconnectPort_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.disconnectPort_but.setObjectName("disconnectPort_but")
                btnRow1.addWidget(self.disconnectPort_but)
                self.serialCol.addLayout(btnRow1)

                self.controlsRow.addLayout(self.serialCol, 2)

                # Calibration controls
                self.calibrationCol = QtWidgets.QVBoxLayout()
                self.calibrationCol.setSpacing(4)
                self.calibration = QtWidgets.QLabel(parent=self.centralwidget)
                font = QtGui.QFont()
                font.setBold(True)
                self.calibration.setFont(font)
                self.calibration.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.calibration.setObjectName("calibration")
                self.calibrationCol.addWidget(self.calibration)

                calibRow = QtWidgets.QHBoxLayout()
                self.calibration_inLine = QtWidgets.QLineEdit(parent=self.centralwidget)
                self.calibration_inLine.setObjectName("calibration_inLine")
                self.calibration_inLine.setPlaceholderText("e.g. 10")
                calibRow.addWidget(self.calibration_inLine)
                self.newtons = QtWidgets.QLabel(parent=self.centralwidget)
                self.newtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.newtons.setObjectName("newtons")
                calibRow.addWidget(self.newtons)
                self.calibrationCol.addLayout(calibRow)

                self.calibration_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.calibration_but.setObjectName("calibration_but")
                self.calibrationCol.addWidget(self.calibration_but)

                self.controlsRow.addLayout(self.calibrationCol, 2)

                # Set speed controls
                self.setSpeedCol = QtWidgets.QVBoxLayout()
                self.setSpeedCol.setSpacing(4)
                self.label = QtWidgets.QLabel(parent=self.centralwidget)
                font2 = QtGui.QFont()
                font2.setBold(True)
                self.label.setFont(font2)
                self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.label.setObjectName("label")
                self.setSpeedCol.addWidget(self.label)

                speedRow = QtWidgets.QHBoxLayout()
                self.setSpeed_inLine = QtWidgets.QLineEdit(parent=self.centralwidget)
                self.setSpeed_inLine.setObjectName("setSpeed_inLine")
                self.setSpeed_inLine.setPlaceholderText("e.g. 3.0")
                speedRow.addWidget(self.setSpeed_inLine)
                self.setSpeedCol.addLayout(speedRow)

                self.setSpeed_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.setSpeed_but.setObjectName("setSpeed_but")
                self.setSpeedCol.addWidget(self.setSpeed_but)

                self.controlsRow.addLayout(self.setSpeedCol, 2)

                # Direction + start/stop
                self.dirCol = QtWidgets.QVBoxLayout()
                self.dirCol.setSpacing(4)
                dirRow = QtWidgets.QHBoxLayout()
                self.changeDirection_inLine = QtWidgets.QLineEdit(parent=self.centralwidget)
                self.changeDirection_inLine.setObjectName("changeDirection_inLine")
                self.changeDirection_inLine.setReadOnly(True)
                dirRow.addWidget(self.changeDirection_inLine)
                self.changeDirection_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.changeDirection_but.setObjectName("changeDirection_but")
                dirRow.addWidget(self.changeDirection_but)
                self.dirCol.addLayout(dirRow)

                self.start_but_2 = QtWidgets.QPushButton(parent=self.centralwidget)
                self.start_but_2.setObjectName("start_but_2")
                self.dirCol.addWidget(self.start_but_2)
                self.stop_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.stop_but.setObjectName("stop_but")
                self.dirCol.addWidget(self.stop_but)

                self.controlsRow.addLayout(self.dirCol, 2)

                self.leftColumn.addLayout(self.controlsRow)

                # Right panel: metrics and button status
                self.rightPanel = QtWidgets.QVBoxLayout()
                self.rightPanel.setSpacing(8)

                # Metrics stack
                self.displacement = QtWidgets.QLabel(parent=self.centralwidget)
                font3 = QtGui.QFont()
                font3.setBold(True)
                self.displacement.setFont(font3)
                self.displacement.setObjectName("displacement")
                self.rightPanel.addWidget(self.displacement)

                self.displacementLCD = QtWidgets.QLCDNumber(parent=self.centralwidget)
                self.displacementLCD.setObjectName("displacementLCD")
                self.rightPanel.addWidget(self.displacementLCD)

                self.speed = QtWidgets.QLabel(parent=self.centralwidget)
                self.speed.setFont(font3)
                self.speed.setObjectName("speed")
                self.rightPanel.addWidget(self.speed)

                self.speedLCD = QtWidgets.QLCDNumber(parent=self.centralwidget)
                self.speedLCD.setObjectName("speedLCD")
                self.rightPanel.addWidget(self.speedLCD)

                self.force = QtWidgets.QLabel(parent=self.centralwidget)
                self.force.setFont(font3)
                self.force.setObjectName("force")
                self.rightPanel.addWidget(self.force)

                self.forceLCD = QtWidgets.QLCDNumber(parent=self.centralwidget)
                self.forceLCD.setObjectName("forceLCD")
                self.rightPanel.addWidget(self.forceLCD)

                self.maxForce = QtWidgets.QLabel(parent=self.centralwidget)
                self.maxForce.setFont(font3)
                self.maxForce.setObjectName("maxForce")
                self.rightPanel.addWidget(self.maxForce)

                self.maxForceLCD = QtWidgets.QLCDNumber(parent=self.centralwidget)
                self.maxForceLCD.setObjectName("maxForceLCD")
                self.rightPanel.addWidget(self.maxForceLCD)

                self.umtkSate = QtWidgets.QLabel(parent=self.centralwidget)
                self.umtkSate.setFont(font3)
                self.umtkSate.setObjectName("umtkSate")
                self.rightPanel.addWidget(self.umtkSate)

                self.textBrowser_2 = QtWidgets.QTextBrowser(parent=self.centralwidget)
                self.textBrowser_2.setObjectName("textBrowser_2")
                fontState = QtGui.QFont()
                fontState.setPointSize(24)
                fontState.setBold(True)
                self.textBrowser_2.setFont(fontState)
                self.textBrowser_2.setFixedHeight(48)
                self.rightPanel.addWidget(self.textBrowser_2)

                self.motorCurrent_label = QtWidgets.QLabel(parent=self.centralwidget)
                self.motorCurrent_label.setFont(font3)
                self.motorCurrent_label.setObjectName("motorCurrent_label")
                self.rightPanel.addWidget(self.motorCurrent_label)

                self.motorCurrent_display = QtWidgets.QLCDNumber(parent=self.centralwidget)
                self.motorCurrent_display.setObjectName("motorCurrent_display")
                self.rightPanel.addWidget(self.motorCurrent_display)

                self.eStop_display = QtWidgets.QPushButton(parent=self.centralwidget)
                self.eStop_display.setEnabled(False)
                self.eStop_display.setObjectName("eStop_display")
                fontE = QtGui.QFont()
                fontE.setPointSize(20)
                fontE.setBold(True)
                self.eStop_display.setFont(fontE)
                self.eStop_display.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed))
                self.eStop_display.setMinimumHeight(50)
                self.rightPanel.addWidget(self.eStop_display)

                # Button status row
                self.buttonStatus = QtWidgets.QHBoxLayout()
                self.buttonStatus.setSpacing(6)
                self.up_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.up_but.setObjectName("up_but")
                self.up_but.setMinimumSize(QtCore.QSize(60, 40))
                self.buttonStatus.addWidget(self.up_but)
                self.down_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.down_but.setObjectName("down_but")
                self.down_but.setMinimumSize(QtCore.QSize(60, 40))
                self.buttonStatus.addWidget(self.down_but)
                self.tare_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.tare_but.setObjectName("tare_but")
                self.tare_but.setMinimumSize(QtCore.QSize(60, 40))
                self.buttonStatus.addWidget(self.tare_but)
                self.start_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.start_but.setObjectName("start_but")
                self.start_but.setMinimumSize(QtCore.QSize(60, 40))
                self.buttonStatus.addWidget(self.start_but)
                self.aux_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.aux_but.setObjectName("aux_but")
                self.aux_but.setMinimumSize(QtCore.QSize(60, 40))
                self.buttonStatus.addWidget(self.aux_but)
                self.rightPanel.addLayout(self.buttonStatus)

                # Add columns to content row
                self.contentRow.addLayout(self.leftColumn, 3)
                self.contentRow.addLayout(self.rightPanel, 1)
                self.mainLayout.addLayout(self.contentRow, 10)

                self.retranslateUi(MainWindow)
                QtCore.QMetaObject.connectSlotsByName(MainWindow)

        def retranslateUi(self, MainWindow):
                _translate = QtCore.QCoreApplication.translate
                MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
                self.bannerName.setText(_translate("MainWindow", "<html><head/><body><p>UNIVERSAL MECHANICAL TESTING KIT</p></body></html>"))

                self.connectPort_but.setText(_translate("MainWindow", "Connect"))
                self.disconnectPort_but.setText(_translate("MainWindow", "Disconnect"))

                self.calibration.setText(_translate("MainWindow", "<html><head/><body><p>Calibration</p></body></html>"))
                self.newtons.setText(_translate("MainWindow", "N"))
                self.calibration_but.setText(_translate("MainWindow", "Calibrate"))

                self.label.setText(_translate("MainWindow", "<html><head/><body><p>Set Speed</p></body></html>"))
                self.setSpeed_but.setText(_translate("MainWindow", "Set Speed"))

                self.changeDirection_but.setText(_translate("MainWindow", "Change Direction"))
                self.start_but_2.setText(_translate("MainWindow", "Start"))
                self.stop_but.setText(_translate("MainWindow", "Stop"))

                self.displacement.setText(_translate("MainWindow", "Displacement:"))
                self.speed.setText(_translate("MainWindow", "Speed:"))
                self.force.setText(_translate("MainWindow", "Force:"))
                self.maxForce.setText(_translate("MainWindow", "Max Force:"))
                self.umtkSate.setText(_translate("MainWindow", "UMTK State:"))
                self.textBrowser_2.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Cantarell'; font-size:24pt; font-weight:700; font-style:normal;\">\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'.AppleSystemUIFont'; font-weight:600;\"><br /></p></body></html>"))
                self.eStop_display.setText(_translate("MainWindow", "Emergency Stop State"))

                self.up_but.setText(_translate("MainWindow", "JOG \nUP"))
                self.down_but.setText(_translate("MainWindow", "JOG \nDOWN"))
                self.tare_but.setText(_translate("MainWindow", "TARE"))
                self.start_but.setText(_translate("MainWindow", "START"))
                self.aux_but.setText(_translate("MainWindow", "AUX"))
