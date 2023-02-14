@echo off
IF EXIST .\trio-ircproxy\venv\Scripts\activate.bat (
    call .\trio-ircproxy\venv\Scripts\activate.bat
    goto end
) ELSE IF NOT [%1]==[] (
    IF EXIST "%*\trio-ircproxy\venv\Scripts\activate.bat" (
        call "%*\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
    ) 
) ELSE IF EXIST "%UserProfile%\trio-ircproxy\trio-ircproxy\" (
        call "%UserProfile%\trio-ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
    ) ELSE IF EXIST "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\" (
        call "%UserProfile%\Documents\trio-ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
        goto end
)
echo ERROR: Run activate.bat while inside the "trio-ircproxy" root directory.
:end
PROMPT=(trio-ircproxy) %_OLD_VIRTUAL_PROMPT%
