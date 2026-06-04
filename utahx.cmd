@echo off
cd /d "%~dp0"
if exist utahx.exe (
    utahx.exe %*
) else if "%~1"=="" (
    py -3.11 utahx_launcher.py
) else (
    py -3.11 -m utahx_cli %*
)
if errorlevel 1 pause
