#!/usr/bin/env python3
"""
Test script to demonstrate CH340 serial port filtering.
"""

import platform
from lib.UMTKSerial import UMTKSerial

def test_ch340_filtering():
    """Test the CH340 port filtering functionality."""
    
    print(f"Testing on: {platform.system()}")
    print("=" * 50)
    
    serial_mgr = UMTKSerial()
    
    # Test with filtering enabled (default)
    print("🔍 CH340 Filtered Ports:")
    filtered_ports = serial_mgr.rescan_serial_ports(show_all=False)
    for port in filtered_ports:
        print(f"  ✓ {port}")
    
    print("\n📋 All Available Ports:")
    all_ports = serial_mgr.rescan_serial_ports(show_all=True) 
    for port in all_ports:
        print(f"  • {port}")
    
    print(f"\nFiltering Results:")
    print(f"  • Filtered: {len(filtered_ports)} ports")
    print(f"  • Total: {len(all_ports)} ports")
    print(f"  • Filtered out: {len(all_ports) - len(filtered_ports)} ports")
    
    # Show what got filtered out
    filtered_out = [p for p in all_ports if p not in filtered_ports]
    if filtered_out:
        print(f"\n🚫 Filtered Out (non-CH340):")
        for port in filtered_out:
            print(f"  ✗ {port}")

if __name__ == "__main__":
    test_ch340_filtering()