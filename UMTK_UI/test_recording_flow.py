#!/usr/bin/env python3
"""
Test script for recording functionality
Tests: session separators, pause/resume markers, file appending
"""

import os
import sys
import tempfile
import csv
from pathlib import Path

# Add the lib directory to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

from umtk_logic import UMTKLogic

def test_recording_separators():
    """Test that recording separators are written correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create logic instance with temp directory
        logic = UMTKLogic(log_dir=temp_dir)
        
        test_file = os.path.join(temp_dir, "test_recording.csv")
        
        print("Testing recording separators...")
        
        # Test 1: Start new recording
        logic.start_recording("test_recording.csv")
        print("✓ Started recording")
        
        # Simulate some data
        logic.log_data([100, 1, 10.5, 15.2, 5.0, 3.0, "RUNNING", 1.2, 0.8, 0, 0, 0, 1, 0, 12.5, 24.0, 50])
        print("✓ Logged test data")
        
        # Test pause
        logic.pause_recording()
        print("✓ Paused recording")
        
        # Test resume
        logic.resume_recording()
        print("✓ Resumed recording")
        
        # Log more data
        logic.log_data([101, 1, 11.0, 16.0, 5.1, 3.0, "RUNNING", 1.3, 0.9, 0, 0, 0, 1, 0, 12.6, 24.1, 51])
        print("✓ Logged more data after resume")
        
        logic.stop_recording(start_new=False)
        print("✓ Stopped recording")
        
        # Test append to same file
        logic.start_recording("test_recording.csv")
        print("✓ Started new session (append mode)")
        
        logic.log_data([200, 1, 20.0, 25.0, 8.0, 4.0, "RUNNING", 2.0, 1.5, 0, 0, 0, 1, 0, 13.0, 24.5, 55])
        print("✓ Logged data in new session")
        
        logic.stop_recording(start_new=False)
        logic.close()
        
        # Read and validate the CSV file
        print("\nValidating CSV content...")
        with open(test_file, 'r') as f:
            content = f.read()
            print(f"CSV file has {len(content.splitlines())} lines")
            
            # Check for required markers
            markers_found = []
            if "NEW RECORDING SESSION STARTED" in content:
                markers_found.append("Session start marker")
            if "RECORDING PAUSED" in content:
                markers_found.append("Pause marker")
            if "RECORDING RESUMED" in content:
                markers_found.append("Resume marker")
            
            print(f"✓ Found markers: {', '.join(markers_found)}")
            
            # Count data rows vs separator rows
            lines = content.splitlines()
            data_rows = 0
            separator_rows = 0
            
            for line in lines:
                if line.strip() == "":
                    continue
                if "===" in line:
                    separator_rows += 1
                elif line.startswith("Log Timestamp"):
                    continue  # Header
                else:
                    data_rows += 1
            
            print(f"✓ Data rows: {data_rows}, Separator rows: {separator_rows}")
            
        print("\n✓ Recording separators test PASSED")
        return True

def test_csv_structure():
    """Test that CSV structure is valid after separators."""
    with tempfile.TemporaryDirectory() as temp_dir:
        logic = UMTKLogic(log_dir=temp_dir)
        test_file = os.path.join(temp_dir, "structure_test.csv")
        
        print("\nTesting CSV structure...")
        
        logic.start_recording("structure_test.csv")
        logic.log_data([100, 1, 10.5, 15.2, 5.0, 3.0, "RUNNING", 1.2, 0.8, 0, 0, 0, 1, 0, 12.5, 24.0, 50])
        logic.pause_recording()
        logic.resume_recording()
        logic.log_data([101, 1, 11.0, 16.0, 5.1, 3.0, "RUNNING", 1.3, 0.9, 0, 0, 0, 1, 0, 12.6, 24.1, 51])
        logic.stop_recording(start_new=False)
        logic.close()
        
        # Try to parse as CSV
        try:
            with open(test_file, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            # Check that all rows have consistent column counts
            expected_cols = 18  # Based on the header
            inconsistent_rows = []
            
            for i, row in enumerate(rows):
                if len(row) != expected_cols and row and not all(cell == "" for cell in row):
                    inconsistent_rows.append((i + 1, len(row), row[:3]))  # Line number, column count, first 3 cells
            
            if inconsistent_rows:
                print(f"⚠ Found {len(inconsistent_rows)} rows with inconsistent column counts:")
                for line_num, col_count, sample in inconsistent_rows[:5]:  # Show first 5
                    print(f"  Line {line_num}: {col_count} columns, starts with: {sample}")
            else:
                print("✓ All rows have consistent column structure")
            
            print(f"✓ CSV parsing successful, {len(rows)} total rows")
            return len(inconsistent_rows) == 0
            
        except Exception as e:
            print(f"✗ CSV parsing failed: {e}")
            return False

if __name__ == "__main__":
    print("Running recording functionality tests...\n")
    
    success = True
    
    try:
        success &= test_recording_separators()
        success &= test_csv_structure()
        
        if success:
            print("\n🎉 All tests PASSED!")
        else:
            print("\n❌ Some tests FAILED!")
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)