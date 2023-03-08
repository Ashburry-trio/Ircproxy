@echo off
cls
echo.
echo Adding terminate_autoanswer = 1 to clink settings file
echo if you do not have clink download the latest setup.exe from https://github.com/chrisant996/clink/releases
if "%1" == "-3.13" goto start
if "%1" == "-3.12" goto start
if "%1" == "-3.11" goto start
if "%1" == "-3.10" goto start
echo.
echo ERROR: You must run install.bat with a python version parameter. Example: "install.bat -3.10" (to -3.13).
goto complete
:start
echo Ctrl+C to Exit
pause
if not exist "%UserProfile%\appdata\local\clink\" (mkdir "%UserProfile%\appdata\local\clink\")
if not exist "%UserProfile%\appdata\local\clink\settings" (echo terminate_autoanswer = 1 >> %userProfile%\appdata\local\clink\settings)
echo Creating virtual environment in folder named "venv" in the trio-ircproxy directory.
py %1 -m venv .\trio-ircproxy\venv
call .\trio-ircproxy\venv\Scripts\activate.bat
echo Install wheel and pip...
pip install wheel
.\trio-ircproxy\venv\Scripts\python.exe -m pip install pip
.\trio-ircproxy\venv\Scripts\python.exe -m pip install --upgrade pip
pip install --upgrade pip
echo Installing requirments via "pip install -r .\trio-ircproxy\requirements.txt"
pip install -r .\trio-ircproxy\requirements.txt
echo.
call runproxy.bat
:complete