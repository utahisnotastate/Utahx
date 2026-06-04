# Build utahx.exe for Windows double-click distribution.
# Requires: pip install pyinstaller

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "Building utahx.exe..."
py -3.11 -m pip install pyinstaller -q
py -3.11 -m PyInstaller `
    --onefile `
    --name utahx `
    --console `
    --hidden-import uvicorn.logging `
    --hidden-import uvicorn.loops `
    --hidden-import uvicorn.loops.auto `
    --hidden-import uvicorn.protocols `
    --hidden-import uvicorn.protocols.http `
    --hidden-import uvicorn.protocols.http.auto `
    --hidden-import uvicorn.protocols.websockets `
    --hidden-import uvicorn.protocols.websockets.auto `
    --hidden-import uvicorn.lifespan `
    --hidden-import uvicorn.lifespan.on `
    utahx_launcher.py

Copy-Item -Force dist\utahx.exe .
Write-Host "Done: $(Resolve-Path utahx.exe)"
