@echo off
cls
echo.
set pythonversion=%1
if defined pythonversion goto :start
echo ERROR: You must run install.bat with a existing python version's numbered parameter. Example: "install.bat -3.19"
echo.
goto complete
:start
echo use Ctrl+C to Exit, any other key will break the pause.
pause
echo Creating virtual environment in folder named "venv", in the trio-ircproxy directory.
py %1 -m venv .\trio-ircproxy\venv
call .\activate.bat
echo Install and upgrading both `wheel` and `pip`...
python.exe -m pip --require-virtualenv install pip
python.exe -m pip --require-virtualenv install --upgrade pip
pip.exe --require-virtualenv install wheel
python.exe -m pip --require-virtualenv install --upgrade wheel
echo Installing requirments via "pip install -r .\trio-ircproxy\requirements.txt"
pip.exe --require-virtualenv install -r .\trio-ircproxy\requirements.txt
echo.
call runproxy.bat
:complete
pause

