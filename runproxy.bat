@echo off
rem Bypass "Terminate Batch Job" prompt.
if "%~1"=="-FIXED_CTRL_C" (
   REM Remove the -FIXED_CTRL_C parameter
   SHIFT
) ELSE (
   REM Run the batch with <NUL and -FIXED_CTRL_C
   CALL <NUL %0 -FIXED_CTRL_C %*
   GOTO EOF
)
echo.
echo Starting trio-ircproxy.py in virtual-environment.
echo While this window is open, the proxy server will
echo be available and running.
echo.
echo Running ".\activate.bat" and "python.exe .\trio-ircproxy\trio-ircproxy.py"
echo please wait...
IF EXIST ".\activate.bat" (
    call ".\activate.bat"
    goto end1
    ) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy-main\" (
        call "%UserProfile%\Documents\trio-ircproxy-main\activate.bat"
        goto end1
    ) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy\" (
        call "%UserProfile%\Documents\trio-ircproxy\activate.bat"
        goto end1
    ) ELSE IF EXIST "%UserProfile%\trio-ircproxy-main\" (
        call "%UserProfile%\trio-ircproxy-main\activate.bat"
        goto end1
)
echo ERROR, unable to find "activate.bat"
goto done
:end1
IF EXIST "trio-ircproxy\trio-ircproxy.py" (
    python.exe trio-ircproxy\trio-ircproxy.py
    goto done
) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy-main\trio-ircproxy\" (
        python.exe "%UserProfile%\Documents\trio-ircproxy-main\trio-ircproxy\trio-ircproxy.py"
        goto done
) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\" (
        python.exe "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\trio-ircproxy.py"
        goto done
) ELSE IF EXIST "%UserProfile%\trio-ircproxy-main\trio-ircproxy\" (
        python.exe "%UserProfile%\trio-ircproxy-main\trio-ircproxy\trio-ircproxy.py"
        goto done
) ELSE IF EXIST "%UserProfile%\trio-ircproxy\trio-ircproxy\" (
        python.exe "%UserProfile%\trio-ircproxy\trio-ircproxy\trio-ircproxy.py"
        goto done
)
echo ERROR, Unable to find "trio-ircproxy.py"
:done
call "deactivate.bat"
echo finished "deactivate.bat"
:EOF