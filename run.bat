@echo off
rem Bypass "Terminate Batch Job" prompt.
if "%~1"=="-FIXED_CTRL_C" (
   REM Remove the -FIXED_CTRL_C parameter
   SHIFT
) ELSE (
   REM Run the batch with <NUL and -FIXED_CTRL_C
   REM Do this until %1 == -'FIXED_CTRL_C'
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
    ) ELSE IF EXIST "%UserProfile%\Documents\Ircproxy-main\" (
        call "%UserProfile%\Documents\Ircproxy-main\activate.bat"
        goto end1
    ) ELSE IF EXIST "%UserProfile%\Documents\Ircproxy\" (
        call "%UserProfile%\Documents\Ircproxy\activate.bat"
        goto end1
    ) ELSE IF EXIST "%UserProfile%\Ircproxy-main\" (
        call "%UserProfile%\Ircproxy-main\activate.bat"
        goto end1
    ) ELSE IF EXIST "%UserProfile%\Ircproxy\" (
        call "%UserProfile%\Ircproxy\activate.bat"
        goto end1

)
echo ERROR, unable to find "activate.bat"
goto done
:end1
IF EXIST ".\trio-ircproxy\trio-ircproxy.py" (
    python.exe .\trio-ircproxy\trio-ircproxy.py
    goto done
) ELSE IF EXIST "%UserProfile%\Documents\Ircproxy-main\trio-ircproxy\" (
        python.exe "%UserProfile%\Documents\Ircproxy-main\trio-ircproxy\trio-ircproxy.py"
        goto done
) ELSE IF EXIST "%UserProfile%\Documents\Ircproxy\trio-ircproxy\" (
        python.exe "%UserProfile%\Documents\Ircproxy\trio-ircproxy\trio-ircproxy.py"
        goto done
) ELSE IF EXIST "%UserProfile%\Ircproxy-main\trio-ircproxy\" (
        python.exe "%UserProfile%\Ircproxy-main\trio-ircproxy\trio-ircproxy.py"
        goto done
) ELSE IF EXIST "%UserProfile%\Ircproxy\trio-ircproxy\" (
        python.exe "%UserProfile%\Ircproxy\trio-ircproxy\trio-ircproxy.py"
        goto done
)
echo ERROR Unable to find "trio-ircproxy.py"
:done
call "deactivate.bat"
echo finished "deactivate.bat"
:EOF