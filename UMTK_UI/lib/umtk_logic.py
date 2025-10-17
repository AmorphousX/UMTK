from __future__ import annotations

import math
from pathlib import Path
from datetime import datetime
import csv
import os
from typing import List, Optional, Sequence, Any

from .UMTKSerial import UMTKSerial as UMTKSerial_t


class UMTKLogic:
    """Encapsulates non-GUI logic: serial comms, logging, data processing state."""

    def __init__(self, log_dir: str | None = None):
        self.desired_speed = 3.0
        self.X: List[float] = []
        self.Y: List[float] = []
        self.UMTKSerial = UMTKSerial_t()
        
        # Recording control
        self.is_recording = False
        self.is_paused = False
        self.record_start_time = None
        self.pause_accumulated = 0.0
        self.pause_started = None
        self.current_filename_override = None

        # Directory for logs (use user home to ensure write permission in packaged apps)
        if log_dir is None:
            log_dir = str(Path.home().joinpath("UMTK_runs"))
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        # Defer log file creation until user presses Record
        self.log_file = None

    # ---------------- Logging -----------------
    def _start_new_log(self):
        # Unified default filename pattern (matches GUI): UMTK_MM-DD_HH-MM-SS.csv
        timestamp = datetime.now().strftime("%m-%d_%H-%M-%S")
        log_file_path = os.path.join(self.log_dir, f"UMTK_{timestamp}.csv")
        log_file = open(log_file_path, "w", newline='')
        csv_writer = csv.writer(log_file)
        csv_writer.writerow([
            "Log Timestamp", "UMTK Time Counter", "Direction", "Position", "Load", "Current Speed", "Set Speed", "State",
            "F_AMPS", "B_AMPS", "BT_Up", "BT_Down", "BT_Tare", "BT_Start", "BT_Aux", "V_Mot", "V_In", "T_Loop"
        ])
        return log_file

    def log_data(self, data: Sequence[Any]):
        # Only log when actively recording and not paused
        if not (self.is_recording and not self.is_paused):
            return
        if self.log_file and data:
            csv_writer = csv.writer(self.log_file)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            csv_writer.writerow([timestamp, *data])

    # --------------- Serial --------------------
    def init_ports(self, show_all: bool = False):
        return self.UMTKSerial.rescan_serial_ports(show_all=show_all)

    def rescan_ports(self, show_all: bool = False):
        return self.UMTKSerial.rescan_serial_ports(show_all=show_all)

    def connect(self, port: str):
        self.UMTKSerial.connect(port)

    def disconnect(self):
        self.UMTKSerial.disconnect()

    def read_serial(self):
        return self.UMTKSerial.readData()

    def write(self, payload: bytes):
        self.UMTKSerial.write(payload)

    # --------------- Commands ------------------
    def command_increase_speed(self):
        self.write(b'U')

    def command_decrease_speed(self):
        self.write(b'D')

    def command_tare(self):
        self.write(b'Tare\n')
        # Removed automatic rotation on TARE; rotation now only occurs explicitly on stop
        # Add TARE marker to log for event trace
        if self.is_recording and self.log_file:
            try:
                csv_writer = csv.writer(self.log_file)
                tare_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([])  # separation
                csv_writer.writerow([f"=== TARE EXECUTED: {tare_timestamp} ===", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])  # match column count
                csv_writer.writerow([])
                self.log_file.flush()
            except Exception:
                pass  # Fail silently if logging unavailable

    def command_set_speed(self, value: float):
        self.write(f'V {value}\n'.encode())

    def command_calibrate(self, raw_value: float):
        # Calculate valid calbration value sign, user should always supply positive number
        cal_command = f'C {str(math.copysign(1, self.Y[-1]) * -1 * self.UMTKSerial.test_direction * raw_value)}\n'.encode()
        print(f"Latest data point: Y={self.Y[-1] if self.Y else 'N/A'}, test_direction={self.UMTKSerial.test_direction}, raw_value={raw_value}")
        print(f"Cal command: {cal_command}")
        self.write(cal_command)

    def command_start(self):
        self.write(b'Begin\n')

    def command_stop(self):
        self.write(b's')

    def command_set_direction_down(self):
        self.write(b'q')

    def command_set_direction_up(self):
        self.write(b'p')

    # --------------- Data Processing -----------
    def reset_graph_data(self):
        self.X = []
        self.Y = []

    def append_point(self, x: float, y: float, max_points: int = 1500, trim_to: int = 1000):
        self.X.append(x)
        self.Y.append(y)
        if len(self.X) > max_points:
            # Remove first (len - trim_to) elements to keep the most recent trim_to elements
            remove_count = len(self.X) - trim_to
            self.X = self.X[remove_count:]
            self.Y = self.Y[remove_count:]

    # --------------- Helpers -------------------
    def _rotate_log(self):
        # Deprecated: rotation disabled. Kept for backward compatibility; does nothing now.
        pass

    # --------------- Recording Control -------------
    def start_recording(self, filename: str | None = None):
        if filename:
            # Handle custom filename with append capability
            if self.log_file:
                self.log_file.close()
            safe_name = filename.strip().replace(' ', '_')
            if not safe_name.lower().endswith('.csv'):
                safe_name += '.csv'
            
            # Check if filename contains a path or is just a filename
            if os.path.sep in safe_name or ('/' in safe_name and os.path.sep == '\\'):
                # User provided full path, use it directly
                log_file_path = safe_name
                # Create directory if it doesn't exist
                dir_path = os.path.dirname(log_file_path)
                if dir_path:
                    os.makedirs(dir_path, exist_ok=True)
            else:
                # User provided just filename, put it in the default log directory
                log_file_path = os.path.join(self.log_dir, safe_name)
            
            # Check if file exists and append with session marker
            file_exists = os.path.exists(log_file_path)
            mode = 'a' if file_exists else 'w'
            
            self.log_file = open(log_file_path, mode, newline='')
            csv_writer = csv.writer(self.log_file)
            
            if not file_exists:
                # Write header for new file
                csv_writer.writerow([
                    "Log Timestamp", "UMTK Time Counter", "Direction", "Position", "Load", "Current Speed", "Set Speed", "State",
                    "F_AMPS", "B_AMPS", "BT_Up", "BT_Down", "BT_Tare", "BT_Start", "BT_Aux", "V_Mot", "V_In", "T_Loop"
                ])
            else:
                # Add session separator with timestamp for existing file
                session_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([])  # Empty row for separation
                csv_writer.writerow([f"=== NEW RECORDING SESSION STARTED: {session_timestamp} ===", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
                csv_writer.writerow([])  # Empty row for separation
                self.log_file.flush()  # Ensure immediate write
            
            self.current_filename_override = safe_name
            print(f"Recording to: {log_file_path} {'(appended)' if file_exists else '(new file)'}")
        else:
            # Do NOT rotate on start. Use existing log file and add a session marker.
            if self.log_file is None:
                # Create a new default file now (first recording)
                self.log_file = self._start_new_log()
            else:
                csv_writer = csv.writer(self.log_file)
                session_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([])  # Empty row for separation
                csv_writer.writerow([f"=== NEW RECORDING SESSION STARTED: {session_timestamp} ===", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
                csv_writer.writerow([])  # Empty row for separation
                self.log_file.flush()  # Ensure immediate write
            self.current_filename_override = None
        import time
        self.is_recording = True
        self.is_paused = False
        self.record_start_time = time.time()
        self.pause_accumulated = 0.0
        self.pause_started = None

    def pause_recording(self):
        if self.is_recording and not self.is_paused:
            import time
            self.is_paused = True
            self.pause_started = time.time()
            
            # Add pause marker to CSV
            if self.log_file:
                csv_writer = csv.writer(self.log_file)
                pause_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([])  # Empty row for separation
                csv_writer.writerow([f"=== RECORDING PAUSED: {pause_timestamp} ===", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
                csv_writer.writerow([])  # Empty row for separation
                self.log_file.flush()  # Ensure immediate write

    def resume_recording(self):
        if self.is_recording and self.is_paused:
            import time
            now = time.time()
            if self.pause_started is not None:
                self.pause_accumulated += now - self.pause_started
            self.pause_started = None
            self.is_paused = False
            
            # Add resume marker to CSV
            if self.log_file:
                csv_writer = csv.writer(self.log_file)
                resume_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                csv_writer.writerow([])  # Empty row for separation
                csv_writer.writerow([f"=== RECORDING RESUMED: {resume_timestamp} ===", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
                csv_writer.writerow([])  # Empty row for separation
                self.log_file.flush()  # Ensure immediate write

    def stop_recording(self, start_new: bool = True):  # start_new retained for API compatibility
        self.is_recording = False
        self.is_paused = False
        self.record_start_time = None
        self.pause_accumulated = 0.0
        self.pause_started = None
        self.current_filename_override = None
        # Write stop marker into existing file (no rotation)
        if self.log_file:
            csv_writer = csv.writer(self.log_file)
            stop_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            csv_writer.writerow([])
            csv_writer.writerow([f"=== RECORDING STOPPED: {stop_timestamp} ===", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
            csv_writer.writerow([])
            self.log_file.flush()

    def elapsed_recording_time(self) -> float:
        import time
        if not self.is_recording or self.record_start_time is None:
            return 0.0
        base = time.time() - self.record_start_time
        if self.is_paused and self.pause_started is not None:
            # Exclude current paused duration
            return base - self.pause_accumulated - (time.time() - self.pause_started)
        return base - self.pause_accumulated

    def close(self):
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    # --------------- Mapping -------------------
    @staticmethod
    def umtk_state_to_str(state: int) -> str:
        mapping = {
            0: "RUNNING",
            1: "IDLE",
            3: "JOG UP",
            4: "JOG DOWN",
            8: "TARE"
        }
        state_name = mapping.get(state, "UNKNOWN")
        return (f"<p align=\"center\" style=\" font-family:'.AppleSystemUIFont'; font-size:20pt; font-weight:600; font-style:normal;\">{state_name}</p>")

