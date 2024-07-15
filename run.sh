@echo off
echo.
echo "Starting trio-ircproxy.py in virtual-environment."
echo "While this window is open, the proxy server will"
echo "be available and running. DO NOT share your port"
echo "numbers, IP address, or login with anybody! Care has been"
echo "taken to NOT let this information leak to the public."
echo.
echo "Calling './activate.sh' and executing 'python .\trio-ircproxy\trio-ircproxy.py'"
echo "please wait while the program loads..."
./activate.sh
python ./trio-ircproxy/trio-ircproxy.py
