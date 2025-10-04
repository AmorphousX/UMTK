import serial
import serial.tools.list_ports
from enum import Enum
import platform


class UMTKSerial:
    class SerialStates(Enum):
        DISCONNECTED = 1
        CONNECTED = 2
        PENDING_CONNECT = 3
        PENDING_DISCONNECT = 4
        ERROR = 5
        FAILED = 6

    known_serial_ports = []
    status_text = "Uninitialized"
    status = SerialStates.DISCONNECTED
    port_name = ""
    handle = ""
    show_all_ports = False

    @staticmethod
    def is_ch340_port(port_info) -> bool:
        """Check if a serial port is likely a CH340 device."""
        system = platform.system().lower()
        
        # Windows: Accept all COM ports (CH340 shows up as COM ports)
        if system == "windows":
            return port_info.device.startswith("COM")
        
        # macOS: Look for CH340 identifiers
        elif system == "darwin":
            # CH340 typically shows up with these patterns on macOS
            ch340_patterns = [
                "usbserial",
                "ch340",
                "CH340",
                "wch.cn",
                "1a86:7523",  # Common CH340 USB ID
                "wchusbserial"
            ]
            port_str = str(port_info).lower()
            description = getattr(port_info, 'description', '') or ''
            manufacturer = getattr(port_info, 'manufacturer', '') or ''
            
            return any(pattern.lower() in port_str or 
                      pattern.lower() in description.lower() or 
                      pattern.lower() in manufacturer.lower() 
                      for pattern in ch340_patterns)
        
        # Linux: Look for CH340 identifiers
        elif system == "linux":
            # CH340 typically shows up with these patterns on Linux
            ch340_patterns = [
                "ch341",
                "ch340", 
                "CH340",
                "1a86:7523",  # Common CH340 USB ID
                "QinHeng Electronics"
            ]
            port_str = str(port_info).lower()
            description = getattr(port_info, 'description', '') or ''
            manufacturer = getattr(port_info, 'manufacturer', '') or ''
            
            return any(pattern.lower() in port_str or 
                      pattern.lower() in description.lower() or 
                      pattern.lower() in manufacturer.lower() 
                      for pattern in ch340_patterns)
        
        # Unknown system: show all ports
        return True

    def init_serial(self) -> list:
        self.status = "Disconnected"
        return self.rescan_serial_ports()

    def rescan_serial_ports(self, show_all: bool = None) -> list:
        """Scan for serial ports, optionally filtering for CH340 devices."""
        if show_all is not None:
            self.show_all_ports = show_all
            
        ports = serial.tools.list_ports.comports()
        self.known_serial_ports = []
        
        if ports:
            for this_port in ports:
                # Apply CH340 filter unless showing all ports
                if self.show_all_ports or self.is_ch340_port(this_port):
                    self.known_serial_ports.append(this_port.device)
        
        # If no ports found after filtering, add a helpful message
        if not self.known_serial_ports:
            if self.show_all_ports:
                self.known_serial_ports.append("NO PORTS AVAILABLE")
            else:
                self.known_serial_ports.append("NO CH340 PORTS FOUND (try 'Show All')")
                
        return self.known_serial_ports
    
    def connect(self, picked_port:str) -> str:
        if picked_port == "NO PORTS AVAILABLE" or picked_port is None:
            return ""
        self.status = self.SerialStates.PENDING_CONNECT
        print(f"Connecting serial port: {picked_port}")

        try:
            self.handle = serial.Serial(picked_port, 250000, timeout=5)
            self.port_name = picked_port
            self.status_text = f"{self.port_name} Connecting..."

            # Set a data rate, default 30hz
            self.write(f'r30\n'.encode())
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
        finally:
            return self.status_text
        
    def disconnect(self) -> str:
        if self.status != self.SerialStates.DISCONNECTED:
            self.status = self.SerialStates.PENDING_DISCONNECT
            print(f"Disconnecting {self.port_name}")
            self.handle.close()
            self.status = f"Disconnected serial port: {self.port_name}"
        else:
            print("Port not connected")
        
        self.port_name = ""
        self.status = self.SerialStates.DISCONNECTED

    def readData(self) -> list:
        if self.handle and self.handle.is_open:
            return_data = []
            try:
                line = self.handle.readline()
                # print(line)
                data = line.decode().strip()
                if data:
                    # print(f"Received: {data}")
                    return_data = self.cast_serial_data(data)
                self.status_text = f"Connected {self.port_name}"
                self.status = self.SerialStates.CONNECTED
            except serial.SerialException as e:
                print(f"Error reading serial port: {e}")
                self.status_text = f"ERROR {self.port_name}"
                self.status = self.SerialStates.ERROR
            except Exception as e:
                print(f"Error opening serial port: {e}")
            finally:
                return return_data
        else:
            self.status_text = "Disconnected"
            self.status = self.SerialStates.DISCONNECTED

    def cast_serial_data(self, in_data):
        return_data = []
        if ("== TARE ==" in in_data):
            # Tare
            print("T", end="", flush="True")
        elif ("DIRECTION" in in_data):
            # Header
            print("H", end="", flush="True")
        elif ("+++" in in_data):
            # Header
            print("S", end="", flush="True")
        else:
            try:
            # Data
                values = list(in_data.split('\t'))
                if len(values) >= 14:
                    i_millis, i_direction, i_position, i_load, i_cur_speed, i_set_speed, i_state, \
                    i_f_amps, i_b_amps, i_bt_up, i_bt_down, i_bt_tare, i_bt_start,\
                    i_bt_aux, i_v_in, i_v_mot, i_t_loop = values
                    
                    millis = int(i_millis)
                    direction = int(i_direction)
                    if direction == 0:
                        position = -1*float(i_position)
                        load = float(i_load)  
                        self.test_direction = -1
                    else:
                        position = float(i_position)
                        load = -1*float(i_load)
                        self.test_direction = 1
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

                    return_data = [millis, direction, position, load, cur_speed, set_speed,
                        state, f_amps, b_amps, bt_up, bt_down, bt_tare,
                        bt_start, bt_aux, v_in, v_mot, t_loop]

            except ValueError as e:
                print(f"Error processing serial data: {e}", flush="True")
                print(in_data)
            finally:
                # print(return_data)
                print(".", end="", flush="True")
                return return_data
            
    def write(self, bytes):
        if self.status in [self.SerialStates.CONNECTED, self.SerialStates.PENDING_CONNECT, self.SerialStates.ERROR]:
            self.handle.write(bytes)
        else:
            print("Send Failed, Port Not Connected")


