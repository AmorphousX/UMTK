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

        # Smart serial port rescanning
        self.rescan_serial_timer = QtCore.QTimer()
        self.rescan_serial_timer.timeout.connect(self._smart_rescan_serial_ports)
        self._update_rescan_interval()  # Set initial interval based on port availability

        # Add recording controls to main UI
        self._setup_recording_controls()
        
        # Ensure large fonts for numeric displays (force override any defaults)
        self._setup_large_fonts()

    def _setup_large_fonts(self):
        """Ensure all numeric displays use large, readable fonts."""
        large_font = QtGui.QFont()
        large_font.setPointSize(64)  # Large but reasonable - 64pt
        large_font.setBold(True)
        
        # Apply large fonts and styling to ensure they're visible
        displays = [
            self.ui.displacementLCD,
            self.ui.speedLCD,
            self.ui.forceLCD,
            self.ui.maxForceLCD,
            self.ui.motorCurrent_display
        ]
        
        for display in displays:
            display.setFont(large_font)
            # Clean styling with white text for better contrast
            display.setStyleSheet("""
                QLabel {
                    font-size: 64pt;
                    font-weight: bold;
                    color: white;
                }
            """)
            # Ensure adequate space for large fonts
            display.setMinimumSize(300, 120)
            display.setMaximumSize(16777215, 16777215)
            display.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        
        print(f"Applied 64pt fonts to all numeric displays")

    def _setup_recording_controls(self):
        """Wire up the recording controls that are already in the UI design."""
        # Amp alert configuration with fading background
        self.AMP_ALERT_THRESHOLD = 5.0  # Amps; adjust as needed
        self._amp_alert_active = False
        self._amp_opacity = 0.0  # Current background opacity (0.0 to 1.0)
        
        # Animation for fading background
        self._amp_fade_animation = QtCore.QPropertyAnimation(self, b"amp_opacity")
        self._amp_fade_animation.setDuration(5000)  # 5 seconds fade
        self._amp_fade_animation.finished.connect(self._clear_amp_alert)
        
        # Connect the file browse button
        self.ui.file_browse_btn.clicked.connect(self._browse_output_file)
        
        # Connect recording buttons
        self.ui.record_toggle_btn.clicked.connect(self._toggle_recording)
        self.ui.record_stop_btn.clicked.connect(self._stop_recording)
        
        # Connect filename validation
        self.ui.filename_edit.textChanged.connect(self._update_recording_button_state)
        
        # Add recording timer for elapsed time updates
        self.recording_timer = QtCore.QTimer()
        self.recording_timer.timeout.connect(self._refresh_recording_elapsed)
        self.recording_timer.start(1000)  # Update every second

        # Wire up show all ports checkbox
        self.ui.showAllPorts_check.stateChanged.connect(self._on_show_all_ports_changed)
        
        # Track dropdown state for smart rescanning
        self.ui.portsDropdown.currentTextChanged.connect(self._on_port_selection_changed)
        
        # Initialize recording button state
        self._update_recording_button_state()
        
        # Set default filename in the edit box
        self.ui.filename_edit.setText(self._generate_default_filename())

    def _is_dropdown_open(self) -> bool:
        """Check if the ports dropdown is currently open."""
        # QComboBox doesn't have a direct "isOpen" method, but we can use view visibility
        return hasattr(self.ui.portsDropdown, 'view') and self.ui.portsDropdown.view().isVisible()

    def _has_valid_ch340_ports(self) -> bool:
        """Check if there are valid CH340 ports available."""
        show_all = self.ui.showAllPorts_check.isChecked()
        ports = self.logic.rescan_ports(show_all=show_all)
        
        # Check if we have real ports (not error messages)
        return any(port not in ["NO PORTS AVAILABLE", "NO CH340 PORTS FOUND (try 'Show All')"] 
                  for port in ports)

    def _generate_default_filename(self) -> str:
        """Generate the default filename that would be used for autogenerated files."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S.%f")[:-3]
        return f"UMTK_run_{timestamp}.csv"

    def _update_filename_after_rotation(self):
        """Update the filename in the file picker after log rotation, but only if using default naming."""
        # Only update if the current filename looks like a default autogenerated name
        current_filename = self.ui.filename_edit.text().strip()
        
        # Check if current filename follows the UMTK_run_ pattern (indicating it's a default)
        if current_filename.startswith("UMTK_run_") and current_filename.endswith(".csv"):
            # Generate new default filename and update the field
            self.ui.filename_edit.textChanged.disconnect(self._update_recording_button_state)
            self.ui.filename_edit.setText(self._generate_default_filename())
            self.ui.filename_edit.textChanged.connect(self._update_recording_button_state)

    def _is_filename_valid(self) -> bool:
        """Check if the current filename is valid for recording."""
        filename = self.ui.filename_edit.text().strip()
        
        # Empty filename is allowed (will use auto-generated name)
        if not filename:
            return True
            
        # Check for invalid characters in filename
        import re
        import os
        
        # Handle directory paths properly
        if os.path.sep in filename or ('/' in filename and os.path.sep == '\\'):
            # This is a full path, validate directory and filename separately
            try:
                dir_path = os.path.dirname(filename)
                file_name = os.path.basename(filename)
                
                # Validate the filename part (not the directory path)
                base_name = file_name
                if base_name.lower().endswith('.csv'):
                    base_name = base_name[:-4]
                    
                # Check for empty filename after removing extension
                if not base_name.strip():
                    return False
                    
                # Check for invalid characters in filename only (not path)
                invalid_chars = r'[<>:"|?*]'  # Removed / and \ since they're valid in paths
                if re.search(invalid_chars, file_name):
                    return False
                    
                # Check for reserved names (Windows) in filename only
                reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                                 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
                                 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
                if base_name.upper() in reserved_names:
                    return False
                
                # Check if directory path is valid (but don't require it to exist yet)
                # We'll let the recording logic handle directory creation
                if dir_path:
                    # Basic path validation - check if it's a reasonable path format
                    try:
                        os.path.normpath(dir_path)  # This will raise if path is malformed
                        # If directory exists, check if it's writable
                        if os.path.exists(dir_path) and not os.access(dir_path, os.W_OK):
                            return False
                    except (OSError, ValueError):
                        return False
                        
                return True
                
            except (OSError, ValueError):
                return False
        else:
            # This is just a filename without path, validate normally
            base_name = filename
            if base_name.lower().endswith('.csv'):
                base_name = base_name[:-4]
                
            # Check for empty name after removing extension
            if not base_name.strip():
                return False
                
            # Check for invalid characters (Windows/Linux/Mac compatible)
            invalid_chars = r'[<>:"/\\|?*]'
            if re.search(invalid_chars, base_name):
                return False
                
            # Check for reserved names (Windows)
            reserved_names = {'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 
                             'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 
                             'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'}
            if base_name.upper() in reserved_names:
                return False
                
        return True

    def _update_recording_button_state(self):
        """Update the enable/disable state of the recording button based on filename validity."""
        # Check if filename field is empty and regenerate default if needed
        current_filename = self.ui.filename_edit.text().strip()
        if not current_filename and not self.logic.is_recording:
            # Temporarily disconnect the signal to avoid recursion
            self.ui.filename_edit.textChanged.disconnect(self._update_recording_button_state)
            self.ui.filename_edit.setText(self._generate_default_filename())
            self.ui.filename_edit.textChanged.connect(self._update_recording_button_state)
        
        # Only validate when not currently recording
        if not self.logic.is_recording:
            is_valid = self._is_filename_valid()
            self.ui.record_toggle_btn.setEnabled(is_valid)
            
            # Optional: Update button style or tooltip to indicate why it's disabled
            if not is_valid:
                self.ui.record_toggle_btn.setToolTip("Invalid filename. Please check for invalid characters or missing directories.")
            else:
                self.ui.record_toggle_btn.setToolTip("Start recording")
        else:
            # Always enable button when recording (for pause/resume functionality)
            self.ui.record_toggle_btn.setEnabled(True)
            self.ui.record_toggle_btn.setToolTip("Pause recording")

    def _update_rescan_interval(self):
        """Update rescan interval based on CH340 port availability."""
        has_valid_ports = self._has_valid_ch340_ports()
        
        if has_valid_ports:
            # Valid ports found: rescan every 2 seconds
            interval = 2000
            scan_status = "Auto-scan: 2s (device ready)"
        else:
            # No valid ports: rescan every 1 second for faster detection
            interval = 1000
            scan_status = "Auto-scan: 1s (waiting for device)"
        
        self.rescan_serial_timer.start(interval)
        
        # Update status to show current scan interval
        current_status = self.logic.UMTKSerial.status_text
        if not current_status.startswith("Scanning"):
            updated_status = f"{current_status} | {scan_status}"
            self.ui.textBrowser.setText(updated_status)
        
    def _smart_rescan_serial_ports(self):
        """Smart rescanning that respects dropdown state and adjusts intervals."""
        # Don't rescan if dropdown is currently open (user is selecting)
        if self._is_dropdown_open():
            return
            
        # Store current selection to preserve it if possible
        current_selection = self.ui.portsDropdown.currentText()
        
        # Show scanning indicator in status
        original_status = self.logic.UMTKSerial.status_text
        self.ui.textBrowser.setText("Scanning for ports...")
        
        # Rescan ports
        self._rescan_serial_ports()
        
        # Try to restore previous selection if it still exists
        if current_selection and not current_selection.startswith("NO "):
            index = self.ui.portsDropdown.findText(current_selection)
            if index >= 0:
                self.ui.portsDropdown.setCurrentIndex(index)
        
        # Update rescan interval based on current port availability
        self._update_rescan_interval()

    def _on_port_selection_changed(self):
        """Called when user changes port selection."""
        # This helps us know when user is actively using the dropdown
        pass

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
        # Update rescan interval since port availability may have changed
        self._update_rescan_interval()

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

        # Update numeric displays (units now in separate labels)
        self.ui.displacementLCD.setText(f"{position:.2f}")
        self.ui.forceLCD.setText(f"{load:.2f}")
        self.ui.speedLCD.setText(f"{cur_speed:.2f}")
        self.ui.textBrowser_2.setHtml(self.logic.umtk_state_to_str(state))
        current_max_force = max(self.logic.Y) if self.logic.Y else load
        self.ui.maxForceLCD.setText(f"{current_max_force:.2f}")
        # Motor current (forward amps primary)
        self.ui.motorCurrent_display.setText(f"{f_amps:.2f}")
        self.ui.changeDirection_inLine.setText("COMPRESSION" if direction == 1 else "TENSILE")

        self.ui.down_but.setStyleSheet(self.theme_btn_green if bt_up else self.theme_btn_red)
        self.ui.up_but.setStyleSheet(self.theme_btn_green if bt_down else self.theme_btn_red)
        self.ui.tare_but.setStyleSheet(self.theme_btn_green if bt_tare else self.theme_btn_red)
        self.ui.start_but.setStyleSheet(self.theme_btn_green if bt_start else self.theme_btn_red)
        self.ui.aux_but.setStyleSheet(self.theme_btn_green if bt_aux else self.theme_btn_red)
        # eStop_display retains its existing visual behavior
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
        self.ui.motorCurrent_display.setText(f"{motor_amps:1.2f}")
        
        if motor_amps >= self.AMP_ALERT_THRESHOLD:
            # Current is above threshold - set to full red immediately
            if not self._amp_alert_active:
                self._amp_alert_active = True
                self._amp_fade_animation.stop()  # Stop any ongoing fade
                self.set_amp_opacity(1.0)  # Full red immediately
        else:
            # Current is below threshold - start fading if alert is active
            if self._amp_alert_active and self._amp_fade_animation.state() != QtCore.QAbstractAnimation.State.Running:
                # Start fading from current opacity to 0
                self._amp_fade_animation.setStartValue(self._amp_opacity)
                self._amp_fade_animation.setEndValue(0.0)
                self._amp_fade_animation.start()

    # ---------------- Command wrappers ---------------
    def _increase_speed(self):
        self.logic.command_increase_speed()

    def _decrease_speed(self):
        self.logic.command_decrease_speed()

    def _tare(self):
        self.logic.command_tare()
        # Update filename in file picker after log rotation (if using default naming)
        self._update_filename_after_rotation()

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
            self._update_recording_button_state()  # Update button state
        elif self.logic.is_paused:
            # Resume recording
            self.logic.resume_recording()
            self.ui.recording_status_label.setText("Recording")
            self.ui.record_toggle_btn.setText("Pause")
            self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
            self._update_recording_button_state()  # Update button state
        else:
            # Pause recording
            self.logic.pause_recording()
            self.ui.recording_status_label.setText("Paused")
            self.ui.record_toggle_btn.setText("Resume")
            self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            self._update_recording_button_state()  # Update button state

    def _stop_recording(self):
        """Stop recording and reset UI."""
        if self.logic.is_recording:
            self.logic.stop_recording(start_new=True)
        self.ui.recording_status_label.setText("Idle")
        self.ui.record_toggle_btn.setText("Start")
        self.ui.record_toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.ui.record_stop_btn.setEnabled(False)
        self.ui.recording_elapsed_label.setText("00:00")
        self._update_recording_button_state()  # Update button state
        # Update filename in file picker after log rotation (if using default naming)
        self._update_filename_after_rotation()

    def _refresh_recording_elapsed(self):
        """Update the elapsed time display."""
        if self.logic.is_recording:
            secs = int(self.logic.elapsed_recording_time())
            mm = secs // 60
            ss = secs % 60
            self.ui.recording_elapsed_label.setText(f"{mm:02d}:{ss:02d}")
        else:
            self.ui.recording_elapsed_label.setText("00:00")

    def _clear_amp_alert(self):
        """Clear the amp alert highlighting after timeout."""
        self._amp_alert_active = False
        self._amp_opacity = 0.0
        self.ui.motorCurrent_display.setStyleSheet("""
                QLabel {
                    font-size: 64pt;
                    font-weight: bold;
                    color: white;
                }
            """)

    # Property for animation system
    def get_amp_opacity(self):
        return self._amp_opacity
    
    def set_amp_opacity(self, opacity):
        self._amp_opacity = opacity
        # Convert opacity to background color with alpha
        if opacity > 0:
            # Red background with varying opacity, preserving large font
            alpha = int(255 * opacity)
            self.ui.motorCurrent_display.setStyleSheet(
                f"background-color: rgba(255, 0, 0, {alpha}); color: white; font-weight: bold; font-size: 64pt;"
            )
        else:
            # Reset to normal large font styling
            self.ui.motorCurrent_display.setStyleSheet("""
                QLabel {
                    font-size: 64pt;
                    font-weight: bold;
                    color: white;
                }
            """)
    
    # Qt property for animation
    amp_opacity = QtCore.pyqtProperty(float, get_amp_opacity, set_amp_opacity) if QT_LIB == "PyQt6" else QtCore.Property(float, get_amp_opacity, set_amp_opacity)

    # ---------------- Qt Overrides --------------------
    def closeEvent(self, event):  # noqa: N802
        self.logic.close()
        event.accept()

