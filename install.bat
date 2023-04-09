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
call .\activate.bat
echo Install wheel and pip...
pip install wheel
python.exe -m pip install pip
python.exe -m pip install --upgrade pip
echo Installing requirments via "pip install -r .\trio-ircproxy\requirements.txt"
pip install -r .\trio-ircproxy\requirements.txt
echo.
echo Running "runproxy.bat" to start the proxy server. User and password is "user : pass" port 4321
echo Make sure you are connected to the internet when you change your login.
call runproxy.bat
:complete