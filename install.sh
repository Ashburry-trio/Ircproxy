#!/bin/bash
# -*- coding: utf-8 -*-
echo "Creating virtual environment in folder named "venv" in the ./trio-ircproxy directory."
echo "Activating virtual environment."
python -m venv ./trio-ircproxy/venv
chmod +x ./trio-ircproxy/venv/bin/activate.sh
chmod +x ./activate.sh
chmod +x ./runproxy.sh
source ./trio-ircproxy/venv/bin/activate.sh
echo "Installing dependencies."
pip install -r ./trio-ircproxy/requirements.txt
source ./runproxy.sh
echo "Done."