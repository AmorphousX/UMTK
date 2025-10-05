#!/usr/bin/env python3
"""
Test script to demonstrate how recording append behavior works.
This shows what happens when you restart recording on the same file.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
from pathlib import Path
from lib.umtk_logic import UMTKLogic

def test_recording_append():
    """Test that restarting recording appends with session markers."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Testing in: {temp_dir}")
        
        # Create logic instance with temp directory
        logic = UMTKLogic(log_dir=temp_dir)
        
        # Test file path
        test_file = os.path.join(temp_dir, "test_recording.csv")
        
        print("\n=== First Recording Session ===")
        logic.start_recording(test_file)
        
        # Simulate some data points
        logic.log_data([0, 1, 10.5, 25.0, 3.0, 3.0, 1, 1.2, 0.8, 0, 0, 0, 1, 0, 12.5, 24.1, 50])
        logic.log_data([100, 1, 11.0, 26.5, 3.0, 3.0, 1, 1.3, 0.9, 0, 0, 0, 1, 0, 12.5, 24.1, 52])
        logic.log_data([200, 1, 11.5, 28.0, 3.0, 3.0, 1, 1.4, 1.0, 0, 0, 0, 1, 0, 12.5, 24.1, 48])
        
        logic.stop_recording()
        print("First session complete")
        
        print("\n=== Second Recording Session (same file) ===")
        # Start recording again with the same filename
        logic.start_recording(test_file)
        
        # Simulate more data points
        logic.log_data([0, 1, 12.0, 30.0, 3.5, 3.5, 1, 1.5, 1.1, 0, 0, 0, 1, 0, 12.5, 24.1, 45])
        logic.log_data([100, 1, 12.5, 32.5, 3.5, 3.5, 1, 1.6, 1.2, 0, 0, 0, 1, 0, 12.5, 24.1, 47])
        
        logic.stop_recording()
        print("Second session complete")
        
        print("\n=== File Contents ===")
        # Show the contents of the file
        with open(test_file, 'r') as f:
            contents = f.read()
            print(contents)
        
        print(f"\nFile saved to: {test_file}")
        print("Notice how the second session is clearly separated with timestamps!")
        
        logic.close()

if __name__ == "__main__":
    test_recording_append()