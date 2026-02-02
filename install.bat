@echo off
cls
echo.
set pythonversion=%1
if defined pythonversion goto :start
echo ERROR: You must run install.bat with a existing python.exe: "install.bat python3.13"
echo.
goto complete
:start
echo use Ctrl+C to EXIT, any other key will INSTALL and RUN Trio-Ircproxy.py
pause
echo Creating virtual environment in folder named "venv", in the trio-ircproxy directory.
%1 -m venv .venv
python.exe -m pip install --upgrade virtualenv
call .\activate.bat
echo Install and upgrading both `wheel` and `pip`...
python.exe -m pip --require-virtualenv install --upgrade pip 
python.exe -m pip --require-virtualenv install --upgrade wheel 
python.exe -m pip --require-virtualenv install --upgrade setuptools
python.exe -m pip --require-virtualenv install --upgrade bulid
echo Installing requirments...
python.exe -m pip --require-virtualenv install -r .\trio-ircproxy\requirements.txt
echo.
call runproxy.bat
:complete
echo You may need to enter the command:
echo Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
echo In your powershell terminal.
pause


