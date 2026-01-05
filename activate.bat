@echo off

IF EXIST ".\trio-ircproxy\venv\Scripts\activate.bat" (
    call ".\trio-ircproxy\venv\Scripts\activate.bat"
    goto end
)
echo ERROR: "install.bat" must first be run after you may execute "runproxy.bat"
goto EOF
:end
PROMPT=(trio-ircproxy) %_OLD_VIRTUAL_PROMPT%
:EOF
