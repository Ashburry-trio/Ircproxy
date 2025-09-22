@echo off
IF EXIST ".\trio-ircproxy\venv\Scripts\activate.bat" (
    call ".\trio-ircproxy\venv\Scripts\activate.bat"
    goto end
) ELSE IF EXIST "%*\trio-ircproxy\venv\Scripts\activate.bat" (
        call "%*\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
) ELSE IF EXIST "%UserProfile%\Ircproxy\trio-ircproxy\" (
        call "%UserProfile%\Ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
) ELSE IF EXIST "%UserProfile%\Ircproxy-main\trio-ircproxy\" (
        call "%UserProfile%\Ircproxy-main\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
) ELSE IF EXIST "%UserProfile%\Documents\Ircproxy\trio-ircproxy\" (
        call "%UserProfile%\Documents\Ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
) ELSE IF EXIST "%UserProfile%\Documents\Ircproxy-main\trio-ircproxy\" (
        call "%UserProfile%\Documents\Ircproxy-main\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
)
echo ERROR: Run activate.bat while inside the "Ircproxy" root directory.
goto EOF
:end
PROMPT=(trio-ircproxy) %_OLD_VIRTUAL_PROMPT%
:EOF
