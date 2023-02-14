@echo off
rem Bypass "Terminate Batch Job" prompt.
if "%~1"=="-FIXED_CTRL_C" (
   REM Remove the -FIXED_CTRL_C parameter
   SHIFT
) ELSE (
   REM Run the batch with <NUL and -FIXED_CTRL_C
   CALL <NUL %0 -FIXED_CTRL_C %*
   GOTO :EOF
)
echo.
echo Starting flask_app.py in virtual-environment.
echo While this window is open, the web-server will
echo be available and running.
echo Edit ".\trio-ircproxy\scripts\www\www-server-config.ini" 
echo to use an valid IP and Port number.
echo.
echo Running "\trio-ircproxy\venv\Scripts\activate.bat" and "python.exe \trio-ircproxy\scripts\www\flask_app.py"
if EXIST .\trio-ircproxy\venv\Scripts\activate.bat (
    call .\trio-ircproxy\venv\Scripts\activate.bat
    goto end1
    ) ELSE IF EXIST "%UserProfile%\trio-ircproxy\trio-ircproxy\" (
        call "%UserProfile%\trio-ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
        goto end1
    ) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\" (
        call "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
        goto end1
)
echo You must call "runweb.bat" from the "trio-ircproxy" root directory after one-time call "install.bat".
goto end
:end1
IF EXIST .\trio-ircproxy\scripts\www\flask_app.py (
    ".\trio-ircproxy\venv\Scripts\python.exe" .\trio-ircproxy\scripts\www\flask_app.py
    goto end
    ) ELSE IF EXIST "%UserProfile%\trio-ircproxy\trio-ircproxy\" (
        "%UserProfile%\trio-ircproxy\trio-ircproxy\venv\Scripts\python.exe" "%UserProfile%\trio-ircproxy\trio-ircproxy\scripts\www\flask_app.py"
        goto end
    ) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\" (
        "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\venv\Scripts\python.exe" "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\scripts\www\flask_app.py"
        goto end
)
echo ERROR: unable to locate ".\trio-ircproxy\scripts\www\flask_app.py"
:end
pause
:done