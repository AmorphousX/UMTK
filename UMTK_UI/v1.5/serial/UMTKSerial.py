import serial
import serial.tools.list_ports
from enum import Enum

class UMTKSerial:
    class SerialStates(Enum):
        DISCONNECTED = 1
        CONNECTED = 2
        PENDING_CONNECT = 3
        PENDING_DISCONNECT = 4

    known_serial_ports = []
    status_text = "Uninitialized"
    status = SerialStates.DISCONNECTED
    port_name = ""
    handle = ""

    class SerialStates(Enum):
        DISCONNECTED = 1
        CONNECTED = 2
        PENDING_CONNECT = 3
        PENDING_DISCONNECT = 4
        ERROR = 5
        FAILED = 6

    def init_serial(self) -> list:
        self.status = "Disconnected"
        return self.rescan_serial_ports()

    def rescan_serial_ports(self) -> list:
        ports = serial.tools.list_ports.comports()
        self.known_serial_ports = []
        if ports:
            for this_port in ports:
                self.known_serial_ports.append(this_port.device)
        else:
            self.known_serial_ports.append("NO PORTS AVAILABLE")
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

            # Set a data rate, default 20hz
            self.write(f'r20\n'.encode())
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
            self.X = []
            self.Y = []
            print("T", end="")
        elif ("DIRECTION" in in_data):
            # Header
            print("H", end="")
        else:
            try:
            # Data
                values = list(in_data.split('\t'))
                if len(values) >= 14:
                    i_direction, i_position, i_load, i_cur_speed, i_set_speed, i_state, \
                    i_f_amps, i_b_amps, i_bt_up, i_bt_down, i_bt_tare, i_bt_start,\
                    i_bt_aux, i_v_in, i_v_mot, i_t_loop = values
                    
                    direction = int(i_direction)
                    if direction == 0:
                        position = -1*float(i_position)
                        load = -1*float(i_load)  
                        self.test_direction = -1
                    else:
                        position = float(i_position)
                        load = float(i_load)
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

                    return_data = [direction, position, load, cur_speed, set_speed,
                        state, f_amps, b_amps, bt_up, bt_down, bt_tare,
                        bt_start, bt_aux, v_in, v_mot, t_loop]

            except ValueError as e:
                print(f"Error processing serial data: {e}")
                print(in_data)
            finally:
                return return_data
            
    def write(self, bytes):
        if self.status in [self.SerialStates.CONNECTED, self.SerialStates.PENDING_CONNECT]:
            self.handle.write(bytes)
        else:
            print("Send Failed, Port Not Connected")


