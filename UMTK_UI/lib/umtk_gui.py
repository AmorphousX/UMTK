from __future__ import annotations

from PyQt6 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from .umtk_design import Ui_MainWindow as UMTK_MainWindow
from .umtk_logic import UMTKLogic
from .theme_manager import ThemeManager
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
    def __init__(self, logic: UMTKLogic, theme: str = "dark"):
        super().__init__()
        self.logic = logic
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        self.current_theme = theme.lower()
        
        # Initialize amp alert opacity (needed for theme application)
        self._amp_opacity = 0.0  # Current background opacity (0.0 to 1.0)
        
        self.ui = UMTK_MainWindow()
        self.ui.setupUi(self)

        # Connect theme toggle button
        self.ui.themeToggleBtn.clicked.connect(self.toggle_theme)

        # Apply initial theme
        self.apply_theme(self.current_theme)

        # Theme-dependent assets and matplotlib style
        if self.current_theme == "dark":
            plt.style.use('dark_background')
            self.dot_color = "yellow"
            self.ui.cat_2.setPixmap(QtGui.QPixmap(resource_path("img/cat_1k_dark.png")))
        else:
            plt.style.use('default')
            self.dot_color = "red"
            self.ui.cat_2.setPixmap(QtGui.QPixmap(resource_path("img/cat_1k.png")))

        # Graph setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Force Displacement Graph")
        self.ax.set_xlabel("Position (mm)")
        self.ax.set_ylabel("Force (N)")
        self.sp, = self.ax.plot([], [], label='', ms=10, color=self.dot_color, marker='.', ls='')
        
        # Minimize borders - reduce margins to bring axes closer to edges
        # Reduced space above title by increasing top margin
        self.figure.subplots_adjust(left=0.02, bottom=0.01, right=0.98, top=0.96)
        
        # Apply initial graph theme
        self._update_graph_theme()
        
        # Set up the graph layout
        self.ui.graphDisplay.setLayout(QtWidgets.QVBoxLayout())
        self.ui.graphDisplay.layout().addWidget(self.canvas)
        
        # Adjust graph layout after a short delay to ensure proper sizing
        QtCore.QTimer.singleShot(100, self._adjust_graph_layout)

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
        
        # Fix initial layout issues (filename box squished at startup)
        # Trigger resize event simulation to activate the existing dynamic sizing system
        QtCore.QTimer.singleShot(50, self._simulate_resize_for_initial_layout)

    # Cache last button and voltage states for theme restyling
    self._btn_state_bt_up = False
    self._btn_state_bt_down = False
    self._btn_state_bt_tare = False
    self._btn_state_bt_start = False
    self._btn_state_bt_aux = False
    self._last_v_mot = None

    def _setup_large_fonts(self):
        """Setup dynamic font sizing for numeric displays."""
        # Store references to large displays for dynamic sizing
        self.large_displays = [
            self.ui.displacementLCD,
            self.ui.speedLCD,
            self.ui.forceLCD,
            self.ui.maxForceLCD,
            self.ui.motorCurrent_display
        ]
        
        for display in self.large_displays:
            # Remove minimum size constraints to allow displays to shrink properly
            # Only set size policy to allow flexible sizing
            display.setMaximumSize(16777215, 16777215)
            display.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        
        # Apply initial dynamic font sizing
        self._update_dynamic_fonts()
        
        # Apply theme-appropriate styling for large displays
        self._apply_large_display_theme()
        
        print(f"Setup dynamic fonts for all numeric displays")

    def _update_dynamic_fonts(self):
        """Update font sizes based on current widget sizes."""
        for display in getattr(self, 'large_displays', []):
            if display.isVisible():
                # Calculate font size based on widget height
                widget_height = display.height()
                # Use approximately 50% of the widget height for font size to prevent overflow
                # Lower minimum to 8pt to handle very small windows, max 80pt
                font_size = max(8, min(80, int(widget_height * 0.5)))
                
                # If widget is very small (less than 30px), use even smaller font
                if widget_height < 30:
                    font_size = max(6, int(widget_height * 0.4))
                
                font = QtGui.QFont()
                font.setPointSize(font_size)
                font.setBold(True)
                display.setFont(font)

    def resizeEvent(self, event):  # noqa: N802
        """Handle window resize events to update dynamic fonts."""
        super().resizeEvent(event)
        # Update fonts after resize with a small delay to ensure widgets have settled
        QtCore.QTimer.singleShot(50, self._update_dynamic_fonts)
        # Also adjust graph layout for better title display on smaller screens
        QtCore.QTimer.singleShot(100, self._adjust_graph_layout)

    def _simulate_resize_for_initial_layout(self):
        """Fix initial layout issues by simulating a resize event to trigger dynamic sizing."""
        try:
            # Get current window size
            current_size = self.size()
            
            # Create a fake resize event with the current size to trigger the existing
            # dynamic sizing system that already works perfectly on resize
            fake_resize_event = QtGui.QResizeEvent(current_size, current_size)
            
            # Send the resize event to ourselves to activate dynamic sizing
            self.resizeEvent(fake_resize_event)
                    
        except Exception as e:
            # Fail silently to avoid disrupting startup
            print(f"Warning: Could not simulate resize for initial layout: {e}")

    def _setup_recording_controls(self):
        """Wire up the recording controls that are already in the UI design."""
        # Amp alert configuration with fading background
        self.AMP_ALERT_THRESHOLD = 5.0  # Amps; adjust as needed
        self._amp_alert_active = False
        
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
        return any(port not in ["NO PORTS AVAILABLE","NO UMTK FOUND (try 'All') "]
                  for port in ports)

    def _generate_default_filename(self) -> str:
        """Generate shortened default filename with full path.

        Format: UMTK_MM-DD_HH-MM-SS.csv placed in ~/UMTK_runs
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
        base_name = f"UMTK_{timestamp}.csv"
        default_dir = Path.home() / "UMTK_runs"
        try:
            default_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass  # Fail silently, UI will still show filename
        return str(default_dir / base_name)


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
            scan_status = "Scanning..."
        else:
            # No valid ports: rescan every 1 second for faster detection
            interval = 1000
            scan_status = "Scanning..."

        self.rescan_serial_timer.start(interval)
        
        # Update status to show current scan interval
        current_status = self.logic.UMTKSerial.status_text
        if not current_status.startswith("Scanning"):
            updated_status = f"{current_status} | {scan_status}"
            self.ui.textBrowser.setText(updated_status)
        
    def _smart_rescan_serial_ports(self):
        """Smart rescanning that respects dropdown state and adjusts intervals."""
        # Don't rescan if already connected
        if self.logic.UMTKSerial.status == self.logic.UMTKSerial.SerialStates.CONNECTED:
            return
            
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
        if direction == 1:
            self.ui.changeDirection_inLine.setText("COMPRESSION")
        elif direction == 0:
            self.ui.changeDirection_inLine.setText("TENSILE")
        else:
            self.ui.changeDirection_inLine.setText("INVALID")

    # Cache states for theme refresh
    self._btn_state_bt_up = bool(bt_up)
    self._btn_state_bt_down = bool(bt_down)
    self._btn_state_bt_tare = bool(bt_tare)
    self._btn_state_bt_start = bool(bt_start)
    self._btn_state_bt_aux = bool(bt_aux)
    self._last_v_mot = v_mot
    self._apply_button_status_styles()
        # eStop_display retains its existing visual behavior
        # eStop styling applied within _apply_button_status_styles for consistency

        if state == 8:  # TARE
            # Removed rotation on TARE; only reset graph data
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
        # No filename rotation anymore; do nothing

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
        # Provide full default path using current default pattern
        default_suggested = self._generate_default_filename()
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Select Output File",
            default_suggested,
            "CSV Files (*.csv);;All Files (*)"
        )
        if filename:
            self.ui.filename_edit.setText(filename)

    def _toggle_recording(self):
        """Start/pause recording based on current state."""
        if not self.logic.is_recording:
            # Start recording
            filename = self.ui.filename_edit.text().strip() or None
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
        # No rotation -> keep filename unchanged

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
        # Use themed amp alert styling
        style = self.get_themed_amp_alert_style(opacity)
        self.ui.motorCurrent_display.setStyleSheet(style)
    
    # Qt property for animation (PyQt6)
    amp_opacity = QtCore.pyqtProperty(float, get_amp_opacity, set_amp_opacity)

    # ---------------- Theme Management --------------------
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_theme = "light" if self.current_theme == "dark" else "dark"
        self.switch_theme(new_theme)
    
    def switch_theme(self, theme_name: str):
        """Switch to the specified theme."""
        if theme_name != self.current_theme:
            self.current_theme = theme_name
            self.apply_theme(theme_name)
            
            # Update matplotlib style and graph colors
            if theme_name == "dark":
                plt.style.use('dark_background')
                self.dot_color = "yellow"
                self.ui.cat_2.setPixmap(QtGui.QPixmap(resource_path("img/cat_1k_dark.png")))
            else:
                plt.style.use('default')
                self.dot_color = "red"
                self.ui.cat_2.setPixmap(QtGui.QPixmap(resource_path("img/cat_1k.png")))
            
            # Update graph plot color and redraw
            if hasattr(self, 'sp'):
                self.sp.set_color(self.dot_color)
                # Update graph background and styling
                self._update_graph_theme()
                self.figure.canvas.draw()
            # Reapply dynamic button styles to ensure text color/background update
            self._apply_button_status_styles()

    def _apply_button_status_styles(self):
        """Reapply styles for interactive buttons and eStop after theme or state changes."""
        # Use cached states (set in _process_serial_data)
        self.ui.down_but.setStyleSheet(self.theme_btn_green if self._btn_state_bt_up else self.theme_btn_red)
        self.ui.up_but.setStyleSheet(self.theme_btn_green if self._btn_state_bt_down else self.theme_btn_red)
        self.ui.tare_but.setStyleSheet(self.theme_btn_green if self._btn_state_bt_tare else self.theme_btn_red)
        self.ui.start_but.setStyleSheet(self.theme_btn_green if self._btn_state_bt_start else self.theme_btn_red)
        self.ui.aux_but.setStyleSheet(self.theme_btn_green if self._btn_state_bt_aux else self.theme_btn_red)
        # eStop
        if self._last_v_mot is not None and self._last_v_mot < 8:
            self.ui.eStop_display.setStyleSheet(self.theme_btn_red)
        else:
            self.ui.eStop_display.setStyleSheet("")
    
    def apply_theme(self, theme_name: str):
        """Apply the specified theme to all UI elements."""
        styles = self.theme_manager.get_theme_styles(theme_name)
        
        # Apply main window style
        self.setStyleSheet(styles["main_window"])
        
        # Update theme toggle button icon and style
        # Use light bulb icon for theme switching (universal theme toggle symbol)
        self.ui.themeToggleBtn.setText("💡")  # Light bulb icon for theme switching
        
        self.ui.themeToggleBtn.setStyleSheet(styles["theme_switcher"])
        
        # Apply styles to other UI elements
        self._apply_theme_to_controls(styles)
        
        # Apply theme to large displays
        self._apply_large_display_theme()
        
        # Update theme-specific button colors
        self._update_theme_button_colors(styles)
    
    def _apply_large_display_theme(self):
        """Apply theme-appropriate styling to large number displays."""
        # Get the appropriate text color for the theme
        text_color = "#ffffff" if self.current_theme == "dark" else "#212121"
        
        # Note: font-size removed from CSS to allow dynamic font sizing
        large_display_style = f"""
            QLabel {{
                font-weight: bold;
                color: {text_color};
                background-color: transparent;
            }}
        """
        
        # Apply to all large displays
        for display in getattr(self, 'large_displays', []):
            # Skip motorCurrent_display if it has amp alert styling
            if display == self.ui.motorCurrent_display and getattr(self, '_amp_opacity', 0) > 0:
                continue  # Let amp alert styling take precedence
            display.setStyleSheet(large_display_style)
        
        # Update dynamic fonts after theme change
        self._update_dynamic_fonts()
    
    def _apply_theme_to_controls(self, styles: dict):
        """Apply theme styles to various UI controls."""
        # Input fields
        input_fields = [self.ui.filename_edit, self.ui.setSpeed_inLine, self.ui.changeDirection_inLine, self.ui.calibration_inLine]
        for widget in input_fields:
            if hasattr(self.ui, widget.objectName()):
                widget.setStyleSheet(styles["input_field"])
        
        # Combo boxes
        if hasattr(self.ui, 'portsDropdown'):
            self.ui.portsDropdown.setStyleSheet(styles["combo_box"])
        
        # Text browsers
        if hasattr(self.ui, 'textBrowser'):
            self.ui.textBrowser.setStyleSheet(styles["text_browser"])
        if hasattr(self.ui, 'textBrowser_2'):
            self.ui.textBrowser_2.setStyleSheet(styles["text_browser"])
        
        # Checkboxes
        if hasattr(self.ui, 'showAllPorts_check'):
            self.ui.showAllPorts_check.setStyleSheet(styles["checkbox"])
        
        # Labels
        for widget in self.findChildren(QtWidgets.QLabel):
            # Skip the large number displays as they have special styling
            if widget.objectName() not in ['displacementLCD', 'speedLCD', 'forceLCD', 'maxForceLCD', 'motorCurrent_display']:
                widget.setStyleSheet(styles["label"])
        
        # Group boxes (including display containers)
        for widget in self.findChildren(QtWidgets.QGroupBox):
            widget.setStyleSheet(styles["groupbox"])
            
        # Buttons - apply theme-appropriate text colors without affecting layout
        button_text_color = "#ffffff" if self.current_theme == "dark" else "#212121"
        for widget in self.findChildren(QtWidgets.QPushButton):
            if widget.objectName() != 'themeToggleBtn':  # Skip theme toggle button as it has special styling
                # Only apply text color, preserve existing button styling and layout
                widget.setStyleSheet(f"QPushButton {{ color: {button_text_color}; }}")
    
    def _update_theme_button_colors(self, styles: dict):
        """Update button color references for theme compatibility."""
        self.theme_btn_red = styles["button_red"]
        self.theme_btn_green = styles["button_green"]
        self.theme_btn_blue = styles["button_blue"]
        self.theme_btn_neutral = styles["button_neutral"]
    
    def get_themed_amp_alert_style(self, opacity: float) -> str:
        """Get the amp alert style for the current theme."""
        amp_styles = self.theme_manager.get_amp_alert_styles(self.current_theme)
        if opacity > 0:
            return amp_styles["alert"].format(opacity=opacity)
        else:
            return amp_styles["normal"]
    
    def _update_graph_theme(self):
        """Update the graph styling to match the current theme."""
        if self.current_theme == "dark":
            # Dark theme - dark background, light text
            self.ax.set_facecolor('#2b2b2b')
            self.figure.patch.set_facecolor('#2b2b2b')
            self.ax.tick_params(colors='white')
            self.ax.xaxis.label.set_color('white')
            self.ax.yaxis.label.set_color('white')
            self.ax.title.set_color('white')
            self.ax.spines['bottom'].set_color('white')
            self.ax.spines['top'].set_color('white')
            self.ax.spines['right'].set_color('white')
            self.ax.spines['left'].set_color('white')
        else:
            # Light theme - match main window background color, dark text
            self.ax.set_facecolor('#f5f5f5')  # Match main window background
            self.figure.patch.set_facecolor('#f5f5f5')  # Match main window background
            self.ax.tick_params(colors='black')
            self.ax.xaxis.label.set_color('black')
            self.ax.yaxis.label.set_color('black')
            self.ax.title.set_color('black')
            self.ax.spines['bottom'].set_color('black')
            self.ax.spines['top'].set_color('black')
            self.ax.spines['right'].set_color('black')
            self.ax.spines['left'].set_color('black')

    def _adjust_graph_layout(self):
        """Adjust graph layout margins based on current display size to prevent title clipping."""
        try:
            if hasattr(self, 'ui') and hasattr(self.ui, 'graphDisplay'):
                # Get the current size of the graph display widget
                widget_height = self.ui.graphDisplay.height()
                widget_width = self.ui.graphDisplay.width()
                
                # Calculate proportional top margin and font size based on widget dimensions
                # Use continuous scaling to avoid clipping at step boundaries
                
                # Define size ranges for smooth scaling (supports larger displays while keeping good text scaling)
                min_height, max_height = 200, 1200  # Expected height range (extended for larger displays)
                min_width, max_width = 300, 1800    # Expected width range (extended for wider displays)
                
                # Normalize dimensions to 0-1 range
                height_ratio = max(0.0, min(1.0, (widget_height - min_height) / (max_height - min_height)))
                width_ratio = max(0.0, min(1.0, (widget_width - min_width) / (max_width - min_width)))
                
                # Calculate top margin: smaller displays need more space (lower top margin)
                # Range from 0.90 (small) to 0.97 (large) for smooth transition
                min_top_margin, max_top_margin = 0.90, 0.97
                top_margin = min_top_margin + (height_ratio * (max_top_margin - min_top_margin))
                
                # Calculate font sizes proportionally based on both dimensions
                size_factor = (height_ratio + width_ratio) / 2  # Average both ratios
                
                # Title font size - made bigger range (10pt to 20pt)
                min_title_fontsize, max_title_fontsize = 10, 20
                title_fontsize = min_title_fontsize + (size_factor * (max_title_fontsize - min_title_fontsize))
                title_fontsize = max(10, min(20, int(title_fontsize)))  # Ensure integer and bounds
                
                # Axis tick font size - scales with graph size (6pt to 14pt)
                min_tick_fontsize, max_tick_fontsize = 6, 14
                tick_fontsize = min_tick_fontsize + (size_factor * (max_tick_fontsize - min_tick_fontsize))
                tick_fontsize = max(6, min(14, int(tick_fontsize)))  # Ensure integer and bounds
                
                # Dynamically compute left and bottom margins to avoid clipping axis labels
                # Base margins scaled by tick font size and relative widget size
                # Left: ensure room for Y tick labels + Y axis label
                # Bottom: ensure room for X tick labels + X axis label

                # Estimate width occupied by y-tick labels (rough heuristic: 0.6 * tick_fontsize pixels per character)
                # Use longest tick label currently visible
                y_tick_texts = [t.get_text() for t in self.ax.get_yticklabels() if t.get_text()]
                if y_tick_texts:
                    longest_y = max(len(s) for s in y_tick_texts)
                else:
                    longest_y = 4  # fallback average length

                # Convert heuristic length to relative figure fraction
                # Assume ~ (tick_fontsize * longest_y * 0.6) pixels; divide by widget_width for fraction
                y_label_pixels = tick_fontsize * longest_y * 0.6
                left_needed_fraction = y_label_pixels / max(widget_width, 1)

                # Add extra space if y-axis label present
                if self.ax.yaxis.get_label().get_text():
                    left_needed_fraction += tick_fontsize * 0.004  # small extra fraction

                # Scale left margin between 0.05 and 0.15
                # Introduce damping for large window sizes so margin shrinks back toward minimum
                base_left = left_needed_fraction + 0.05
                # Damping factor: as both ratios approach 1.0, subtract up to 0.04
                damping = 0.04 * ((height_ratio + width_ratio) / 2)
                left_margin = base_left - damping
                left_margin = min(0.15, max(0.05, left_margin))

                # Bottom margin calculation similar for x-axis
                x_tick_texts = [t.get_text() for t in self.ax.get_xticklabels() if t.get_text()]
                if x_tick_texts:
                    longest_x = max(len(s) for s in x_tick_texts)
                else:
                    longest_x = 3

                x_label_pixels = tick_fontsize * longest_x * 0.5
                bottom_needed_fraction = x_label_pixels / max(widget_height, 1)
                if self.ax.xaxis.get_label().get_text():
                    bottom_needed_fraction += tick_fontsize * 0.003

                bottom_margin = min(0.14, max(0.06, bottom_needed_fraction + 0.04))

                # Ensure margins do not crowd the right/top
                right_margin = 0.98
                # Adjust right margin slightly if left is large to maintain aspect (optional subtle tweak)
                if left_margin > 0.13:
                    right_margin = 0.975

                self.figure.subplots_adjust(left=left_margin, bottom=bottom_margin, right=right_margin, top=top_margin)
                
                # Set the title font size
                self.ax.title.set_fontsize(title_fontsize)
                
                # Set axis tick font sizes
                self.ax.tick_params(axis='both', which='major', labelsize=tick_fontsize)
                self.ax.tick_params(axis='both', which='minor', labelsize=max(4, tick_fontsize - 2))
                
                # Redraw the canvas to apply changes
                self.canvas.draw_idle()
                
        except Exception as e:
            # Fail silently to avoid disrupting the UI
            print(f"Warning: Could not adjust graph layout: {e}")

    # ---------------- Qt Overrides --------------------
    def closeEvent(self, event):  # noqa: N802
        self.logic.close()
        event.accept()

