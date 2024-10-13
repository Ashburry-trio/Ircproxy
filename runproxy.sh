#!/bin/bash
echo "You must run this app while in the root directory of"
echo "the Ircproxy project. It should be at /home/<username>/Ircproxy"
echo -
echo "Setting permissions..."
chmod +x ./activate.sh
chmod +x ./run.sh
chmod +x ./runproxy.sh
chmod +x ./install.sh
read -p "Press Enter to continue..."
echo "Activating the virtual-environment..."
source ./activate.sh
read -p "Press Enter to continue..."
python ./trio-ircproxy/trio-ircproxy.py
