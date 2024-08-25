@echo off
echo.
echo "Starting Trio-ircProxy.py in a virtual-environment."
echo "While this window is open, the proxy server will ofc"
echo "be available and running. DO NOT share your server's"
echo "port numbers or IP address nor passwords with anybody!"
echo "-"
chho "You must run this app while in the root directory of"
echo "the Ircproxy project. Usually it is at /home/<username>/Ircproxy"
echo.
echo "Calling 'source ./activate.sh' and executing 'python ./trio-ircproxy/trio-ircproxy.py'"
echo "please wait while the program loads..."
chmod +x ./activate.sh
source ./activate.sh
python ./trio-ircproxy/trio-ircproxy.py
