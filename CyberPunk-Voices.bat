@echo off
:: Disables display of commands in the console

:: Comment: Script to start CyberPunk-Voices
:: This script runs the main Python file (main.py) using python.exe

:: Change to the project directory, if necessary
:: cd "Path\To\Directory\CyberPunk-Voices"

:: Checks if python.exe is available in the PATH
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or is not in the PATH.
    pause
    exit /b 1
)

:: Start the Python script
echo Launch of CyberPunk-Voices...
python.exe main.py

:: Pause to keep the window open if an error occurs
if errorlevel 1 (
    echo An error occurred while executing main.py.
    pause
)