from __future__ import annotations

try:
    from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore
    QT_LIB = "PyQt6"
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
except ImportError:
    from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore
    QT_LIB = "PySide6"
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .umtk_logic import UMTKLogic
from .umtk_design import Ui_MainWindow as UMTK_MainWindow
from .record_dialog import RecordingDialog
from pathlib import Path
import os


def resource_path(relative_path: str) -> str:
    import sys
    try:
        base_path = Path(getattr(sys, "_MEIPASS"))  # type: ignore[attr-defined]
    except Exception:
        base_path = Path(__file__).resolve().parent.parent  # up to v1.5/
    return str(base_path.joinpath(relative_path))


class UMTKWindow(QtWidgets.QMainWindow):
    def __init__(self, logic: UMTKLogic, theme: str = "Dark"):
        super().__init__()
        self.logic = logic
        self.theme = theme
        self.theme_btn_red = "background-color: red"
        self.theme_btn_green = "background-color: green"

        self.ui = UMTK_MainWindow()
        self.ui.setupUi(self)

        # Theme-dependent assets and matplotlib style
        if theme == "Dark":
            plt.style.use('dark_background')
            dot_color = "yellow"
            self.ui.cat_2.setPixmap(QtGui.QPixmap(resource_path("img/cat_1k_dark.png")))
        else:
            dot_color = "blue"
            self.ui.cat_2.setPixmap(QtGui.QPixmap(resource_path("img/cat_1k.png")))

        # Graph setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Force Displacement Graph")
        self.ax.set_xlabel("Displacement (mm)")
        self.ax.set_ylabel("Force (N)")
        self.sp, = self.ax.plot([], [], label='', ms=10, color=dot_color, marker='.', ls='')
        self.figure.tight_layout()
        self.ui.graphDisplay.setLayout(QtWidgets.QVBoxLayout())
        self.ui.graphDisplay.layout().addWidget(self.canvas)

        # Wire signals to logic wrappers
        self.ui.connectPort_but.pressed.connect(self._connect_serial_port)
        self.ui.disconnectPort_but.pressed.connect(self._disconnect_serial_port)
        self.ui.up_but.pressed.connect(self._increase_speed)
        self.ui.up_but.released.connect(self._stop_motor)
        self.ui.up_but.setAutoRepeat(True)
        self.ui.up_but.setAutoRepeatDelay(100)
        self.ui.down_but.pressed.connect(self._decrease_speed)
        self.ui.down_but.released.connect(self._stop_motor)
        self.ui.down_but.setAutoRepeat(True)
        self.ui.down_but.setAutoRepeatDelay(100)
        self.ui.tare_but.clicked.connect(self._tare)
        self.ui.start_but.clicked.connect(self._start_motor)
        self.ui.start_but_2.clicked.connect(self._start_motor)
        self.ui.stop_but.clicked.connect(self._stop_motor)
        self.ui.aux_but.clicked.connect(self._stop_motor)
        self.ui.aux_but.released.connect(self._stop_motor)
        self.ui.setSpeed_but.clicked.connect(self._commit_speed)
        self.ui.calibration_but.pressed.connect(self._commit_calibrate)
        self.ui.changeDirection_but.clicked.connect(self._toggle_direction)

        # Initial serial population
        self._initialize_serial_port()
        
        # Set Serial Rate to 25Hz
        self.logic.write(b'r20\n')

        QtCore.QTimer().singleShot(100, self._read_serial)

        self.rescan_serial_timer = QtCore.QTimer()
        self.rescan_serial_timer.timeout.connect(self._rescan_serial_ports)
        self.rescan_serial_timer.start(10000)

        # Add recording controls to main UI
        self._setup_recording_controls()

    def _setup_recording_controls(self):
        """Wire up the recording controls that are already in the UI design."""
        # Connect the file browse button
        self.ui.file_browse_btn.clicked.connect(self._browse_output_file)
        
        # Connect recording buttons
        self.ui.record_toggle_btn.clicked.connect(self._toggle_recording)
        self.ui.record_stop_btn.clicked.connect(self._stop_recording)
        
        # Add recording timer for elapsed time updates
        self.recording_timer = QtCore.QTimer()
        self.recording_timer.timeout.connect(self._refresh_recording_elapsed)
        self.recording_timer.start(1000)  # Update every second

        # Wire up show all ports checkbox
        self.ui.showAllPorts_check.stateChanged.connect(self._on_show_all_ports_changed)

    # ---------------- Serial & UI sync -----------------
    def _initialize_serial_port(self):
        self.ui.portsDropdown.clear()
        show_all = self.ui.showAllPorts_check.isChecked()
        self.ui.portsDropdown.addItems(self.logic.init_ports(show_all=show_all))
        self.ui.textBrowser.setText(self.logic.UMTKSerial.status_text)

    def _rescan_serial_ports(self):
        self.ui.portsDropdown.clear()
        show_all = self.ui.showAllPorts_check.isChecked()
        self.ui.portsDropdown.addItems(self.logic.rescan_ports(show_all=show_all))
        self.ui.textBrowser.setText(self.logic.UMTKSerial.status_text)

    def _on_show_all_ports_changed(self):
        """Handle when the show all ports checkbox is toggled."""
        self._rescan_serial_ports()

    def _connect_serial_port(self):
        picked_port = self.ui.portsDropdown.currentText()
        self.logic.connect(picked_port)
        self.ui.textBrowser.setText(self.logic.UMTKSerial.status_text)

    def _disconnect_serial_port(self):
        self.logic.disconnect()
        self.ui.textBrowser.setText(self.logic.UMTKSerial.status_text)

    def _read_serial(self):
        data = self.logic.read_serial()
        self.ui.textBrowser.setText(self.logic.UMTKSerial.status_text)
        self._process_serial_data(data)
        if data:
            # Logging now gated by logic.is_recording and is_paused inside log_data
            self.logic.log_data(data)
            QtCore.QTimer().singleShot(25, self._read_serial)
        else:
            QtCore.QTimer().singleShot(150, self._read_serial)

    # ---------------- Data Processing ------------------
    def _process_serial_data(self, data):
        if not data:
            return
        millis, direction, position, load, cur_speed, set_speed, state, f_amps, b_amps, \
            bt_up, bt_down, bt_tare, bt_start, bt_aux, \
            v_in, v_mot, t_loop = data

        self.ui.displacementLCD.display(position)
        self.ui.forceLCD.display(load)
        self.ui.speedLCD.display(cur_speed)
        self.ui.textBrowser_2.setHtml(self.logic.umtk_state_to_str(state))
        self.ui.maxForceLCD.display(max(self.logic.Y) if self.logic.Y else load)
        self.ui.changeDirection_inLine.setText("COMPRESSION" if direction == 1 else "TENSILE")

        self.ui.down_but.setStyleSheet(self.theme_btn_green if bt_up else self.theme_btn_red)
        self.ui.up_but.setStyleSheet(self.theme_btn_green if bt_down else self.theme_btn_red)
        self.ui.tare_but.setStyleSheet(self.theme_btn_green if bt_tare else self.theme_btn_red)
        self.ui.start_but.setStyleSheet(self.theme_btn_green if bt_start else self.theme_btn_red)
        self.ui.aux_but.setStyleSheet(self.theme_btn_green if bt_aux else self.theme_btn_red)
        if v_mot < 8:
            self.ui.eStop_display.setStyleSheet(self.theme_btn_red)
        else:
            self.ui.eStop_display.setStyleSheet("")

        if state == 8:  # TARE
            # Only rotate log if actively recording (maintain previous behavior within session)
            if self.logic.is_recording and not self.logic.is_paused:
                self.logic._rotate_log()
            self.logic.reset_graph_data()
        else:
            self.logic.append_point(position, load)
            self.sp.set_data(self.logic.X, self.logic.Y)
            self.ax.set_xlim(min(min(self.logic.X), -10), max(max(self.logic.X), 10))
            self.ax.set_ylim(min(min(self.logic.Y), -10), max(max(self.logic.Y), 10))
        self.figure.canvas.draw()

        motor_amps = (f_amps + b_amps)
        self.ui.motorCurrent_display.display(f"{motor_amps:1.2f}")
        self.ui.motorCurrent_display.setStyleSheet("" if motor_amps < 4 else self.theme_btn_red)

    # ---------------- Command wrappers ---------------
    def _increase_speed(self):
        self.logic.command_increase_speed()

    def _decrease_speed(self):
        self.logic.command_decrease_speed()

    def _tare(self):
        self.logic.command_tare()

    def _commit_speed(self):
        try:
            speed_val = float(self.ui.setSpeed_inLine.text())
            self.logic.command_set_speed(speed_val)
        except Exception:
            print("Error parsing set speed")

    def _commit_calibrate(self):
        try:
            raw = float(self.ui.calibration_inLine.text())
            self.logic.command_calibrate(raw)
        except Exception:
            print("Error parsing calibration load")

    def _start_motor(self):
        self.logic.command_start()

    def _stop_motor(self):
        self.logic.command_stop()

    def _toggle_direction(self):
        if self.ui.changeDirection_inLine.text() == "COMPRESSION":
            self.logic.command_set_direction_up()
        else:
            self.logic.command_set_direction_down()
        QtCore.QTimer().singleShot(100, self._tare)

    # ---------------- Recording Controls ----------------
    def _browse_output_file(self):
        """Open file dialog to select output file location."""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            str(Path.home() / "UMTK_data.csv"),  # Default filename
            "CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            self.ui.filename_edit.setText(filename)

    def _toggle_recording(self):
        """Start/pause recording based on current state."""
        if not self.logic.is_recording:
            # Start recording
            filename = self.ui.filename_edit.text().strip() or None
            
            # Check if file exists and warn user about appending
            if filename and Path(filename).exists():
                reply = QtWidgets.QMessageBox.question(
                    self,
                    "File Exists",
                    f"The file '{Path(filename).name}' already exists.\n\n"
                    "New data will be APPENDED to the existing file with a timestamp marker.\n"
                    "Each recording session will be clearly separated.\n\n"
                    "Continue with recording?",
                    QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                    QtWidgets.QMessageBox.StandardButton.Yes
                )
                if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                    return
            
            self.logic.start_recording(filename)
            self.ui.recording_status_label.setText("Recording")
            self.ui.record_toggle_btn.setText("Pause")
            self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
            self.ui.record_stop_btn.setEnabled(True)
        elif self.logic.is_paused:
            # Resume recording
            self.logic.resume_recording()
            self.ui.recording_status_label.setText("Recording")
            self.ui.record_toggle_btn.setText("Pause")
            self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
        else:
            # Pause recording
            self.logic.pause_recording()
            self.ui.recording_status_label.setText("Paused")
            self.ui.record_toggle_btn.setText("Resume")
            self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))

    def _stop_recording(self):
        """Stop recording and reset UI."""
        if self.logic.is_recording:
            self.logic.stop_recording(start_new=True)
        self.ui.recording_status_label.setText("Idle")
        self.ui.record_toggle_btn.setText("Start")
        self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.ui.record_stop_btn.setEnabled(False)
        self.ui.recording_elapsed_label.setText("00:00")

    def _refresh_recording_elapsed(self):
        """Update the elapsed time display."""
        if self.logic.is_recording:
            secs = int(self.logic.elapsed_recording_time())
            mm = secs // 60
            ss = secs % 60
            self.ui.recording_elapsed_label.setText(f"{mm:02d}:{ss:02d}")
        else:
            self.ui.recording_elapsed_label.setText("00:00")

    # ---------------- Qt Overrides --------------------
    def closeEvent(self, event):  # noqa: N802
        self.logic.close()
        event.accept()

