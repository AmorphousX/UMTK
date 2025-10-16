# UMTK UI - macOS Installation Guide

## Architecture Selection

**Important**: Download the correct version for your Mac:

- **Apple Silicon Macs** (M1, M2, M3, etc.): Download `umtk-ui-macos-arm64.zip`
- **Intel Macs** (2020 and earlier): Download `umtk-ui-macos-intel.zip`
- **Not sure?**: Click Apple menu → About This Mac. If you see "Apple M1/M2/M3", use arm64. If you see "Intel", use intel.

**Wrong architecture error**: If you see "Bad CPU type" or "cannot be opened", you downloaded the wrong architecture.

## Running Unsigned Applications on macOS

This application is not code-signed by Apple, so you may encounter Gatekeeper warnings. Here are several ways to run it:

### Method 1: Use the Install Script (Recommended)
1. Double-click `install.command` 
2. The script will automatically remove quarantine attributes
3. If prompted, allow Terminal to access files
4. After installation, use `start_ui.command` to launch

### Method 2: Manual Quarantine Removal
If you see "App is damaged and can't be opened" or similar:

```bash
# Open Terminal and navigate to the app folder
cd /path/to/umtk-ui-folder

# Remove quarantine attributes
sudo xattr -dr com.apple.quarantine .

# Make scripts executable
chmod +x *.command
```

### Method 3: System Preferences Override
1. Try to open the app (it will fail)
2. Go to **System Preferences** → **Security & Privacy** → **General**
3. Click **"Open Anyway"** next to the blocked app message
4. Confirm when prompted

### Method 4: Right-Click Override
1. Right-click the app or script
2. Select **"Open"** from context menu
3. Click **"Open"** in the security dialog

### Method 5: Disable Gatekeeper (Not Recommended)
```bash
# Disable Gatekeeper (requires admin password)
sudo spctl --master-disable

# Re-enable later for security
sudo spctl --master-enable
```

## If You Still Have Issues

### Python-Related Errors
- The install script will handle Python installation automatically
- It checks for compatible Python versions (3.8+) before installing
- Creates an isolated virtual environment to avoid conflicts

### Permission Errors
```bash
# Make sure scripts are executable
chmod +x install.command start_ui.command

# If needed, run with explicit bash
bash install.command
```

### Homebrew Issues
If Homebrew installation fails:
```bash
# Install Homebrew manually first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Then run the install script again
./install.command
```

## Quick Start
1. Download and extract the UMTK UI package
2. Double-click `install.command` (allow Terminal access if prompted)
3. Wait for installation to complete
4. Double-click `start_ui.command` to launch the application

## Security Note
These methods bypass Apple's security checks. Only do this for software you trust. The UMTK UI source code is available for review on GitHub.

## Troubleshooting
- **"Permission denied"**: Make sure scripts are executable with `chmod +x *.command`
- **"Python not found"**: Run the install script, it will install Python automatically
- **"App damaged"**: Remove quarantine attributes with `xattr -dr com.apple.quarantine .`
- **Still blocked**: Try System Preferences → Security & Privacy → General → "Open Anyway"