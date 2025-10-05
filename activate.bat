@echo off

IF EXIST "%UserProfile%\Ircproxy\trio-ircproxy\venv\Scripts\activate.bat" (
    call "%UserProfile%\Ircproxy\trio-ircproxy\venv\Scripts\activate.bat"
    goto end
)
echo ERROR: "install.bat" must first be run from "%UserProfile%\Ircproxy\install.bat" after you may execute "runproxy.bat"
goto EOF
:end
PROMPT=(trio-ircproxy) %_OLD_VIRTUAL_PROMPT%
:EOF
