@echo off

IF EXIST ".\trio-ircproxy\venv\Scripts\activate.ps1" (
    call ".\trio-ircproxy\venv\Scripts\activate.ps1"
    goto end
)
echo ERROR: "install.bat" must first be run first, after you may execute "runproxy.bat"
goto EOF
:end
PROMPT=(trio-ircproxy) %_OLD_VIRTUAL_PROMPT%
:EOF

