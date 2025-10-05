#!/usr/bin/env python3
"""
Test script to verify CH340 filtering with USB port support on Linux.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.UMTKSerial import UMTKSerial
import serial.tools.list_ports
import platform

def test_usb_filtering():
    """Test that USB ports are detected on Linux."""
    print(f"Platform: {platform.system()}")
    print("=" * 50)
    
    # Get all ports
    all_ports = serial.tools.list_ports.comports()
    print(f"All available ports ({len(all_ports)}):")
    for port in all_ports:
        print(f"  {port.device} - {port.description}")
    
    print("\n" + "=" * 50)
    
    # Test CH340 filtering
    umtk_serial = UMTKSerial()
    
    print("CH340 filtered ports:")
    for port in all_ports:
        is_ch340 = umtk_serial.is_ch340_port(port)
        status = "✓ INCLUDED" if is_ch340 else "✗ FILTERED OUT"
        print(f"  {port.device} - {status}")
        if "usb" in port.device.lower():
            print(f"    → USB port detected in device name")
    
    print("\n" + "=" * 50)
    
    # Test the rescan method
    filtered_ports = umtk_serial.rescan_serial_ports(show_all=False)
    print(f"Final filtered port list: {filtered_ports}")

if __name__ == "__main__":
    test_usb_filtering()