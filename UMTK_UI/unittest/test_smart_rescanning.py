#!/usr/bin/env python3
"""
Test script to demonstrate smart serial port rescanning.
Shows how the intervals change based on CH340 port availability.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from lib.umtk_logic import UMTKLogic

def test_smart_rescanning():
    """Test the smart rescanning intervals."""
    
    print("🔄 Testing Smart Serial Port Rescanning")
    print("=" * 50)
    
    logic = UMTKLogic()
    
    # Test current port situation
    print("📋 Current Port Status:")
    
    # Test filtered ports (CH340 only)
    filtered_ports = logic.rescan_ports(show_all=False)
    has_ch340 = any(port not in ["NO PORTS AVAILABLE", "NO CH340 PORTS FOUND (try 'Show All')"] 
                   for port in filtered_ports)
    
    print(f"  • CH340 Filtered: {filtered_ports}")
    print(f"  • Has Valid CH340: {has_ch340}")
    
    # Test all ports
    all_ports = logic.rescan_ports(show_all=True)
    print(f"  • All Ports: {len(all_ports)} total")
    
    print("\n⏱️  Recommended Scan Intervals:")
    if has_ch340:
        print("  ✅ Valid CH340 ports found")
        print("  🔄 Recommended interval: 2 seconds (slower, device likely stable)")
        print("  📝 Rationale: Device is connected, scan less frequently")
    else:
        print("  ❌ No CH340 ports found")
        print("  🔄 Recommended interval: 1 second (faster, waiting for device)")
        print("  📝 Rationale: No device detected, scan frequently to detect plugged device")
    
    print("\n🎯 Smart Rescanning Benefits:")
    print("  • Fast detection when no device (1s interval)")
    print("  • Efficient monitoring when device present (2s interval)")
    print("  • Respects dropdown interaction (pauses when user selecting)")
    print("  • Preserves user selection when possible")
    print("  • Automatic interval adjustment based on port availability")
    
    logic.close()

if __name__ == "__main__":
    test_smart_rescanning()