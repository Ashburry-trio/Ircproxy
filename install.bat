@echo off
cls
echo.
if "%1" == "-3.11.15" goto start
if "%1" == "-3.10" goto start
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
python.exe -m pip --require-virtualenv install pip
python.exe -m pip --require-virtualenv install --upgrade pip
pip --require-virtualenv install wheel
echo Installing requirments via "pip install -r .\trio-ircproxy\requirements.txt"
pip --require-virtualenv install -r .\trio-ircproxy\requirements.txt
echo.
echo Running "runproxy.bat" to start the proxy server. User and password is "user : pass" port 4321
call runproxy.bat
:complete
pause
