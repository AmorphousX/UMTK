Param(
    [string]$Python = "python",
    [string]$DistDir = "dist/umtk-ui-windows",
    [string]$WorkDir = "build/pyi-win",
    [switch]$OneFile
)

$ErrorActionPreference = 'Stop'

# Ensure we run from v1.5 root
Set-Location (Split-Path -Path $MyInvocation.MyCommand.Path -Parent | Split-Path -Parent | Split-Path -Parent)

# Create venv for reproducible build
if (!(Test-Path .venv-win)) {
  & $Python -m venv .venv-win
}

. .\.venv-win\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

$onefileFlag = ""
if ($OneFile) { $onefileFlag = "--onefile" }

# Collect data folders
$datas = @(
  "img;img",
  "style;style",
  "lib;lib",
  "UMTK_Design.ui;.",
  "UMTK_Design_dynamic.ui;.",
  "requirements.txt;."
) | ForEach-Object { "--add-data `"$_`"" }

pyinstaller $onefileFlag `
  --name UMTK_UI `
  --noconfirm `
  --windowed `
  --hidden-import PyQt6 `
  --hidden-import PySide6 `
  --collect-submodules matplotlib `
  --collect-data matplotlib `
  --collect-data qt_material `
  --distpath $DistDir `
  --workpath $WorkDir `
  @datas `
  main.py

Write-Host "Build complete. Output in $DistDir"
