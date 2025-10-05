@echo off
rem Bypass "Terminate Batch Job" prompt.
if "%~1"=="-FIXED_CTRL_C" (
   REM Remove the -FIXED_CTRL_C parameter
   SHIFT
) ELSE (
   REM Run the batch with <NUL and -FIXED_CTRL_C
   REM the code below this line runs once
   CALL <NUL %0 -FIXED_CTRL_C %*
   GOTO EOF
)
echo.
echo Starting Trio-ircProxy.py in a virtual-environment.
echo While this window is open, the proxy server will ofc
echo be available and running. DO NOT share your server's
echo port numbers or IP address nor passwords with anybody!
echo.
echo Calling ".\activate.bat" and executing "python.exe .\trio-ircproxy\trio-ircproxy.py"
echo please wait...
IF EXIST ".\activate.bat" (
    call ".\activate.bat"
    goto end1
    )
 ELSE IF EXIST "%UserProfile%\Ircproxy\activate.bat" (
        call "%UserProfile%\Ircproxy\activate.bat"
        goto end1
)
echo ERROR, unable to find "%UserProfile%\Ircproxy\activate.bat"
goto done
:end1
IF EXIST ".\trio-ircproxy\trio-ircproxy.py" (
    python.exe .\trio-ircproxy\trio-ircproxy.py
    goto done
) ELSE IF EXIST "%UserProfile%\Ircproxy\trio-ircproxy\trio-ircproxy.py" (
        python.exe "%UserProfile%\Ircproxy\trio-ircproxy\trio-ircproxy.py"
        goto done
)
echo ERROR Unable to find "%USERPROFILE%\trio-ircproxy\trio-ircproxy.py"
:done
call "deactivate.bat"
echo finished "deactivate.bat"
:EOF
prompt