#!/usr/bin/env python3
"""
Test script for WCH340 serial port detection on Windows.
This script will show detailed information about all available serial ports
and demonstrate the improved CH340/WCH detection logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from UMTKSerial import UMTKSerial
import serial.tools.list_ports
import platform

def test_serial_detection():
    print(f"Platform: {platform.system()}")
    print("=" * 60)
    
    # Get all available ports
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("No serial ports found.")
        return
    
    print(f"Found {len(ports)} serial port(s):")
    print()
    
    # Test each port with debug info
    for i, port in enumerate(ports, 1):
        print(f"Port {i}:")
        UMTKSerial.debug_port_info(port)
        
        # Test our detection logic
        is_ch340 = UMTKSerial.is_ch340_port(port)
        print(f"CH340 Detection: {'✓ YES' if is_ch340 else '✗ NO'}")
        print()
    
    # Show filtered results
    print("Filtered Results (CH340 detection enabled):")
    print("-" * 40)
    
    umtk_serial = UMTKSerial()
    umtk_serial.show_all_ports = False
    filtered_ports = umtk_serial.rescan_serial_ports(debug=False)
    
    if filtered_ports:
        for port in filtered_ports:
            print(f"  {port}")
    else:
        print("  No CH340 ports detected")
    
    print()
    print("All Ports (no filtering):")
    print("-" * 25)
    
    umtk_serial.show_all_ports = True
    all_ports = umtk_serial.rescan_serial_ports(debug=False)
    
    for port in all_ports:
        print(f"  {port}")

if __name__ == "__main__":
    test_serial_detection()