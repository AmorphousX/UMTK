"""
Chatgpu made layout dynamic
"""

from PyQt6 import QtCore, QtGui, QtWidgets


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

                # Theme toggle button (right side of banner, bottom aligned)
                self.themeToggleBtn = QtWidgets.QPushButton(parent=self.centralwidget)
                self.themeToggleBtn.setText("🌙")  # Moon icon for dark mode (default)
                self.themeToggleBtn.setObjectName("themeToggleBtn")
                self.themeToggleBtn.setFixedSize(40, 40)
                font_theme = QtGui.QFont()
                font_theme.setPointSize(16)
                self.themeToggleBtn.setFont(font_theme)
                self.themeToggleBtn.setToolTip("Switch between light and dark theme")
                self.topBanner.addWidget(self.themeToggleBtn, 0, QtCore.Qt.AlignmentFlag.AlignBottom)

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
                self.controlsRow.setSpacing(6)  # Reduced from 8 to 6 for more compactness

                # Connection controls group
                connectionGroup = QtWidgets.QGroupBox("Connection")
                connectionGroup.setObjectName("connectionGroup")
                self.serialCol = QtWidgets.QVBoxLayout(connectionGroup)
                self.serialCol.setSpacing(3)  # Reduced from 4 to 3
                
                # Serial device picker and checkbox in same row
                devicePickerRow = QtWidgets.QHBoxLayout()
                self.portsDropdown = QtWidgets.QComboBox(parent=self.centralwidget)
                self.portsDropdown.setObjectName("portsDropdown")
                devicePickerRow.addWidget(self.portsDropdown)

                # Show all ports checkbox with shortened name
                self.showAllPorts_check = QtWidgets.QCheckBox("All")
                self.showAllPorts_check.setObjectName("showAllPorts_check")
                self.showAllPorts_check.setToolTip("Show all serial ports (unchecked: CH340 only)")
                devicePickerRow.addWidget(self.showAllPorts_check)
                self.serialCol.addLayout(devicePickerRow)

                self.textBrowser = QtWidgets.QTextBrowser(parent=self.centralwidget)
                self.textBrowser.setObjectName("textBrowser")
                self.textBrowser.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed))
                self.textBrowser.setFixedHeight(28)  # Reduced from 40 to 28
                self.serialCol.addWidget(self.textBrowser)

                btnRow1 = QtWidgets.QHBoxLayout()
                self.connectPort_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.connectPort_but.setObjectName("connectPort_but")
                btnRow1.addWidget(self.connectPort_but)
                self.disconnectPort_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.disconnectPort_but.setObjectName("disconnectPort_but")
                btnRow1.addWidget(self.disconnectPort_but)
                self.serialCol.addLayout(btnRow1)

                self.controlsRow.addWidget(connectionGroup, 2)

                # Calibration controls group
                calibrationGroup = QtWidgets.QGroupBox("Calibration")
                calibrationGroup.setObjectName("calibrationGroup")
                self.calibrationCol = QtWidgets.QVBoxLayout(calibrationGroup)
                self.calibrationCol.setSpacing(2)  # Reduced from 3 to 2 to make room for larger requirements text

                # Reference Force label
                self.referenceForceLabel = QtWidgets.QLabel("Reference Force:")
                self.referenceForceLabel.setObjectName("referenceForceLabel")
                self.calibrationCol.addWidget(self.referenceForceLabel)

                calibRow = QtWidgets.QHBoxLayout()
                self.calibration_inLine = QtWidgets.QLineEdit(parent=self.centralwidget)
                self.calibration_inLine.setObjectName("calibration_inLine")
                self.calibration_inLine.setPlaceholderText("min: 500")
                calibRow.addWidget(self.calibration_inLine)
                self.newtons = QtWidgets.QLabel(parent=self.centralwidget)
                self.newtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.newtons.setObjectName("newtons")
                calibRow.addWidget(self.newtons)
                self.calibrationCol.addLayout(calibRow)

                # Add small validation requirements label
                self.calibrationRequirementsLabel = QtWidgets.QLabel("Ref > 500 ; 400 < Load < 2000")
                self.calibrationRequirementsLabel.setObjectName("calibrationRequirementsLabel")
                self.calibrationRequirementsLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
                self.calibrationCol.addWidget(self.calibrationRequirementsLabel)

                # Add stretcher to push button to bottom
                self.calibrationCol.addStretch()

                self.calibration_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.calibration_but.setObjectName("calibration_but")
                self.calibration_but.setMinimumHeight(28)  # Reduced from 40 to 28
                self.calibrationCol.addWidget(self.calibration_but)

                self.controlsRow.addWidget(calibrationGroup, 2)

                # Set Speed controls group
                setSpeedGroup = QtWidgets.QGroupBox("Set Speed")
                setSpeedGroup.setObjectName("setSpeedGroup")
                self.setSpeedCol = QtWidgets.QVBoxLayout(setSpeedGroup)
                self.setSpeedCol.setSpacing(3)  # Reduced from 4 to 3

                # Desired Speed label
                self.desiredSpeedLabel = QtWidgets.QLabel("Desired Speed (mm/s)")
                self.desiredSpeedLabel.setObjectName("desiredSpeedLabel")
                self.setSpeedCol.addWidget(self.desiredSpeedLabel)

                speedRow = QtWidgets.QHBoxLayout()
                self.setSpeed_inLine = QtWidgets.QLineEdit(parent=self.centralwidget)
                self.setSpeed_inLine.setObjectName("setSpeed_inLine")
                self.setSpeed_inLine.setPlaceholderText("0.1 - 3.5")
                speedRow.addWidget(self.setSpeed_inLine)
                self.setSpeedCol.addLayout(speedRow)

                # Add speed requirements label
                self.speedRequirementsLabel = QtWidgets.QLabel("Min Speed: 0.1 mm/s")
                self.speedRequirementsLabel.setObjectName("speedRequirementsLabel")
                self.speedRequirementsLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
                self.setSpeedCol.addWidget(self.speedRequirementsLabel)

                # Add stretcher to push button to bottom
                self.setSpeedCol.addStretch()

                self.setSpeed_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.setSpeed_but.setObjectName("setSpeed_but")
                self.setSpeed_but.setMinimumHeight(28)  # Reduced from 40 to 28
                self.setSpeedCol.addWidget(self.setSpeed_but)

                self.controlsRow.addWidget(setSpeedGroup, 2)

                # Direction Control group
                directionGroup = QtWidgets.QGroupBox("Run Control")
                directionGroup.setObjectName("directionGroup")
                self.dirCol = QtWidgets.QVBoxLayout(directionGroup)
                self.dirCol.setSpacing(3)  # Reduced from 4 to 3
                
                dirRow = QtWidgets.QHBoxLayout()
                self.changeDirection_inLine = QtWidgets.QLineEdit(parent=self.centralwidget)
                self.changeDirection_inLine.setObjectName("changeDirection_inLine")
                self.changeDirection_inLine.setReadOnly(True)
                dirRow.addWidget(self.changeDirection_inLine)
                self.changeDirection_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.changeDirection_but.setObjectName("changeDirection_but")
                self.changeDirection_but.setMinimumHeight(28)  # Reduced from 40 to 28
                dirRow.addWidget(self.changeDirection_but)
                self.dirCol.addLayout(dirRow)

                self.start_but_2 = QtWidgets.QPushButton(parent=self.centralwidget)
                self.start_but_2.setObjectName("start_but_2")
                # Use same reduced-height style as other vertical group buttons
                self.start_but_2.setMinimumHeight(28)  # Reduced from 40 to 28
                self.dirCol.addWidget(self.start_but_2)
                self.stop_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.stop_but.setObjectName("stop_but")
                self.stop_but.setMinimumHeight(28)  # Reduced from 40 to 28
                self.dirCol.addWidget(self.stop_but)

                self.controlsRow.addWidget(directionGroup, 2)

                self.leftColumn.addLayout(self.controlsRow)

                # Right panel: recording controls first, then metrics and button status
                self.rightPanel = QtWidgets.QVBoxLayout()
                self.rightPanel.setSpacing(8)

                # Recording controls group
                self.recordingGroupBox = QtWidgets.QGroupBox("Recording Controls")
                self.recordingGroupBox.setObjectName("recordingGroupBox")
                # Set minimum height to ensure buttons remain usable when window is small
                self.recordingGroupBox.setMinimumHeight(120)
                
                recordingGroupLayout = QtWidgets.QVBoxLayout(self.recordingGroupBox)
                
                # File selection layout
                fileSelectionLayout = QtWidgets.QHBoxLayout()
                outputFileLabel = QtWidgets.QLabel("Output File:")
                outputFileLabel.setObjectName("outputFileLabel")
                fileSelectionLayout.addWidget(outputFileLabel)
                
                self.filename_edit = QtWidgets.QLineEdit()
                self.filename_edit.setObjectName("filename_edit")
                self.filename_edit.setPlaceholderText("Choose file location...")
                self.filename_edit.setReadOnly(True)
                fileSelectionLayout.addWidget(self.filename_edit)
                
                self.file_browse_btn = QtWidgets.QPushButton("Browse...")
                self.file_browse_btn.setObjectName("file_browse_btn")
                fileSelectionLayout.addWidget(self.file_browse_btn)
                recordingGroupLayout.addLayout(fileSelectionLayout)
                
                # Status layout
                statusLayout = QtWidgets.QHBoxLayout()
                statusTextLabel = QtWidgets.QLabel("Status:")
                statusTextLabel.setObjectName("statusTextLabel")
                statusLayout.addWidget(statusTextLabel)
                
                self.recording_status_label = QtWidgets.QLabel("Idle")
                self.recording_status_label.setObjectName("recording_status_label")
                statusLayout.addWidget(self.recording_status_label)
                
                statusSpacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
                statusLayout.addItem(statusSpacer)
                
                timeTextLabel = QtWidgets.QLabel("Time:")
                timeTextLabel.setObjectName("timeTextLabel")
                statusLayout.addWidget(timeTextLabel)
                
                self.recording_elapsed_label = QtWidgets.QLabel("00:00")
                self.recording_elapsed_label.setObjectName("recording_elapsed_label")
                font_elapsed = QtGui.QFont()
                font_elapsed.setBold(True)
                self.recording_elapsed_label.setFont(font_elapsed)
                statusLayout.addWidget(self.recording_elapsed_label)
                recordingGroupLayout.addLayout(statusLayout)
                
                # Recording buttons layout
                recordingButtonsLayout = QtWidgets.QHBoxLayout()
                self.record_toggle_btn = QtWidgets.QPushButton("Start")
                self.record_toggle_btn.setObjectName("record_toggle_btn")
                recordingButtonsLayout.addWidget(self.record_toggle_btn)
                
                self.record_stop_btn = QtWidgets.QPushButton("Stop")
                self.record_stop_btn.setObjectName("record_stop_btn")
                self.record_stop_btn.setEnabled(False)
                recordingButtonsLayout.addWidget(self.record_stop_btn)
                recordingGroupLayout.addLayout(recordingButtonsLayout)
                
                self.rightPanel.addWidget(self.recordingGroupBox)

                # Metrics stack
                # Font for metric labels  
                font3 = QtGui.QFont()
                font3.setBold(True)
                
                # Displacement metrics with QGroupBox container
                displacementContainer = QtWidgets.QGroupBox("Displacement (mm)")
                displacementContainer.setObjectName("displacementContainer")
                displacementContainerLayout = QtWidgets.QVBoxLayout(displacementContainer)
                displacementContainerLayout.setContentsMargins(4, 4, 4, 4)
                displacementContainerLayout.setSpacing(2)

                # Large number display (no header needed as title is in GroupBox)
                self.displacementLCD = QtWidgets.QLabel(parent=self.centralwidget)
                self.displacementLCD.setObjectName("displacementLCD")
                font_disp = QtGui.QFont(); font_disp.setPointSize(64); font_disp.setBold(True)
                self.displacementLCD.setFont(font_disp)
                self.displacementLCD.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.displacementLCD.setText("0.00")
                displacementContainerLayout.addWidget(self.displacementLCD)

                self.rightPanel.addWidget(displacementContainer)

                # Speed metrics with QGroupBox container
                speedContainer = QtWidgets.QGroupBox("Speed (mm/s)")
                speedContainer.setObjectName("speedContainer")
                speedContainerLayout = QtWidgets.QVBoxLayout(speedContainer)
                speedContainerLayout.setContentsMargins(4, 4, 4, 4)
                speedContainerLayout.setSpacing(2)

                # Large number display (no header needed as title is in GroupBox)
                self.speedLCD = QtWidgets.QLabel(parent=self.centralwidget)
                self.speedLCD.setObjectName("speedLCD")
                font_speed = QtGui.QFont(); font_speed.setPointSize(64); font_speed.setBold(True)
                self.speedLCD.setFont(font_speed)
                self.speedLCD.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.speedLCD.setText("0.00")
                speedContainerLayout.addWidget(self.speedLCD)

                self.rightPanel.addWidget(speedContainer)

                # Force metrics with QGroupBox container
                forceContainer = QtWidgets.QGroupBox("Force (N)")
                forceContainer.setObjectName("forceContainer")
                forceContainerLayout = QtWidgets.QVBoxLayout(forceContainer)
                forceContainerLayout.setContentsMargins(4, 4, 4, 4)
                forceContainerLayout.setSpacing(2)

                # Large number display (no header needed as title is in GroupBox)
                self.forceLCD = QtWidgets.QLabel(parent=self.centralwidget)
                self.forceLCD.setObjectName("forceLCD")
                font_force = QtGui.QFont(); font_force.setPointSize(64); font_force.setBold(True)
                self.forceLCD.setFont(font_force)
                self.forceLCD.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.forceLCD.setText("0.00")
                forceContainerLayout.addWidget(self.forceLCD)

                self.rightPanel.addWidget(forceContainer)

                # Max Force metrics with QGroupBox container
                maxForceContainer = QtWidgets.QGroupBox("Max Force (N)")
                maxForceContainer.setObjectName("maxForceContainer")
                maxForceContainerLayout = QtWidgets.QVBoxLayout(maxForceContainer)
                maxForceContainerLayout.setContentsMargins(4, 4, 4, 4)
                maxForceContainerLayout.setSpacing(2)

                # Large number display (no header needed as title is in GroupBox)
                self.maxForceLCD = QtWidgets.QLabel(parent=self.centralwidget)
                self.maxForceLCD.setObjectName("maxForceLCD")
                font_max = QtGui.QFont(); font_max.setPointSize(64); font_max.setBold(True)
                self.maxForceLCD.setFont(font_max)
                self.maxForceLCD.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.maxForceLCD.setText("0.00")
                maxForceContainerLayout.addWidget(self.maxForceLCD)

                self.rightPanel.addWidget(maxForceContainer)

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
                # Hide scroll bars since this should always be a single line
                self.textBrowser_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.textBrowser_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                self.rightPanel.addWidget(self.textBrowser_2)

                # Motor Current metrics with QGroupBox container
                motorCurrentContainer = QtWidgets.QGroupBox("Motor Current (A)")
                motorCurrentContainer.setObjectName("motorCurrentContainer")
                motorCurrentContainerLayout = QtWidgets.QVBoxLayout(motorCurrentContainer)
                motorCurrentContainerLayout.setContentsMargins(4, 4, 4, 4)
                motorCurrentContainerLayout.setSpacing(2)

                # Large number display (no header needed as title is in GroupBox)
                self.motorCurrent_display = QtWidgets.QLabel(parent=self.centralwidget)
                self.motorCurrent_display.setObjectName("motorCurrent_display")
                font_amp = QtGui.QFont(); font_amp.setPointSize(64); font_amp.setBold(True)
                self.motorCurrent_display.setFont(font_amp)
                self.motorCurrent_display.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.motorCurrent_display.setText("0.00")
                motorCurrentContainerLayout.addWidget(self.motorCurrent_display)

                self.rightPanel.addWidget(motorCurrentContainer)

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
                self.up_but.setMinimumSize(QtCore.QSize(60, 20))
                self.buttonStatus.addWidget(self.up_but)
                self.down_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.down_but.setObjectName("down_but")
                self.down_but.setMinimumSize(QtCore.QSize(60, 20))
                self.buttonStatus.addWidget(self.down_but)
                self.tare_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.tare_but.setObjectName("tare_but")
                self.tare_but.setMinimumSize(QtCore.QSize(60, 20))
                self.buttonStatus.addWidget(self.tare_but)
                self.start_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.start_but.setObjectName("start_but")
                self.start_but.setMinimumSize(QtCore.QSize(60, 20))
                self.buttonStatus.addWidget(self.start_but)
                self.aux_but = QtWidgets.QPushButton(parent=self.centralwidget)
                self.aux_but.setObjectName("aux_but")
                self.aux_but.setMinimumSize(QtCore.QSize(60, 20))
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

                # Group titles are set in QGroupBox constructors, only set individual control text
                self.newtons.setText(_translate("MainWindow", "N"))
                self.calibration_but.setText(_translate("MainWindow", "Calibrate"))

                self.setSpeed_but.setText(_translate("MainWindow", "Set Speed"))

                self.changeDirection_but.setText(_translate("MainWindow", "Change Direction"))
                self.start_but_2.setText(_translate("MainWindow", "Start"))
                self.stop_but.setText(_translate("MainWindow", "Stop"))

                # Display container titles are set in the QGroupBox constructors, no need to set them here
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

                self.up_but.setText(_translate("MainWindow", "UP"))
                self.down_but.setText(_translate("MainWindow", "DOWN"))
                self.tare_but.setText(_translate("MainWindow", "TARE"))
                self.start_but.setText(_translate("MainWindow", "START"))
                self.aux_but.setText(_translate("MainWindow", "AUX"))
