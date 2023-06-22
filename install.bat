@echo off
cls
echo.
if "%1" == "-3.13" goto start
if "%1" == "-3.12" goto start
if "%1" == "-3.11" goto start
if "%1" == "-3.10" goto start
if "%1" == "-3.9" goto start
if "%1" == "-3.8" goto start
echo.
echo ERROR: You must run install.bat with a python version parameter. Example: "install.bat -3.8" (to -3.13).
goto complete
:start
echo Ctrl+C to Exit
pause
echo Creating virtual environment in folder named "venv" in the trio-ircproxy directory.
py %1 -m venv .\trio-ircproxy\venv
call .\activate.bat
echo Install wheel and pip...
python.exe -m pip install pip
python.exe -m pip install --upgrade pip
pip install wheel
echo Installing requirments via "pip install -r .\trio-ircproxy\requirements.txt"
pip install -r .\trio-ircproxy\requirements.txt
echo.
echo Running "runproxy.bat" to start the proxy server. User and password is "user : pass" port 4321
call runproxy.bat
:complete
pause
