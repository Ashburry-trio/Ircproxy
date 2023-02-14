@echo off
cls
echo.
echo Starting "runweb.bat" and "runproxy.bat" in the current directory in two seperate cmd.exe windows.
echo Please leave these new windows open, they may look unresponsive but are actually functioning normally.
echo You may close this command prompt window.
echo.
start runweb.bat
start runproxy.bat
pause