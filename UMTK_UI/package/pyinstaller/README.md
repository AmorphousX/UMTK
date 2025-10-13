# Packaging UMTK UI with PyInstaller

This produces self-contained app bundles that include a private Python interpreter and all dependencies. Users do not need system Python.

## Prereqs
- Build on each target OS for best results.
- Windows: PowerShell, Python 3.11+, MSVC runtime (installed by Python).
- macOS: Xcode CLT, Python 3.11+.

## Build steps

### Windows
Run in PowerShell from `v1.5/package/pyinstaller`:

- One-folder (faster startup, a directory with EXE):
  `./build_windows.ps1`
- One-file (single EXE, slower startup):
  `./build_windows.ps1 -OneFile`

Artifacts: `v1.5/dist/umtk-ui-windows/UMTK_UI.exe` or single EXE.

### macOS
Run in bash from `v1.5/package/pyinstaller`:

- One-folder:
  `ONEFILE=0 ./build_macos.sh`
- One-file app bundle:
  `ONEFILE=1 ./build_macos.sh`

Artifacts: `v1.5/dist/umtk-ui-mac/UMTK_UI.app` (or a single binary when onefile).

## Signing and notarization (macOS)
To avoid Gatekeeper warnings:
- Create a Developer ID Application cert and sign the app:
  `codesign --deep --force --options=runtime --sign "Developer ID Application: Your Name (TEAMID)" dist/umtk-ui-mac/UMTK_UI.app`
- Zip and notarize via notarytool.

## Shipping
- Zip the `dist/umtk-ui-windows` folder (include all files) and share it.
- For macOS, zip the `.app` bundle or make a DMG.

## Notes
- The app auto-tries PyQt6, then PySide6. Ensure at least one is installed during build. The `requirements.txt` includes PyQt6 by default.
- We added a resource helper so images/styles load in packaged builds.
- If matplotlib backends or missing plugins occur, add `--collect-submodules` and `--collect-data` as above.
