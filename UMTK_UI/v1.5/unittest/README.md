# UMTK Unit Tests

This directory contains test scripts to verify various functionality of the UMTK UI application.

## Test Files

### `test_amp_fading.py`
Tests the new amp alert fading functionality and larger font sizes. Verifies the opacity animation system and UI improvements.

### `test_ch340_filter.py`
Tests the CH340 serial port filtering functionality. Shows which ports are detected as CH340 devices and which are filtered out.

### `test_recording_append.py`
Demonstrates how the recording append behavior works when restarting recording on the same file. Shows session demarcation and timestamp handling.

### `test_smart_rescanning.py`
Tests the smart serial port rescanning logic that adjusts scan intervals based on CH340 port availability (1s when no device, 2s when present).

### `test_usb_filtering.py`
Verifies that USB ports (like `/dev/ttyUSB0` on Linux) are correctly detected by the CH340 filter, including the new USB pattern matching.

## Running Tests

To run any test, use the Python virtual environment:

```bash
cd v1.5/unittest
source ../../.venv/bin/activate  # or use your virtual environment activation method
python test_filename.py
```

Or with the full path:
```bash
cd v1.5/unittest
/home/mding/Documents/amx/github/UMTK/UMTK_UI/.venv/bin/python test_filename.py
```

## Requirements

All tests require the same dependencies as the main application (see `../requirements.txt`).