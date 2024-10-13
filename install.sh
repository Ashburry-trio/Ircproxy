#!/bin/bash

echo "Creating virtual environment in folder named venv, in the trio-ircproxy directory."
python3 -m venv ./trio-ircproxy/venv

# Change permissions for scripts
echo "Setting execute permissions for scripts..."
chmod +x ./activate.sh
chmod +x ./runproxy.sh
chmod +x ./run.sh
chmod +x ./trio-ircproxy/venv/bin/activate.sh
read -p "Press Enter to continue..."  # Wait for user input

# Activate the virtual environment
echo "Activating the virtual environment..."
source ./activate.sh
read -p "Press Enter to continue..."  # Wait for user input

# Upgrade pip and install wheel
echo "Installing and upgrading both wheel and pip..."
python -m pip --require-virtualenv install pip
python -m pip --require-virtualenv install --upgrade pip
pip --require-virtualenv install wheel
python -m pip --require-virtualenv install --upgrade wheel
read -p "Press Enter to continue..."  # Wait for user input

# Install requirements
echo "Installing requirements..."
pip --require-virtualenv install -r ./trio-ircproxy/requirements.txt
read -p "Press Enter to continue..."  # Wait for user input

# Run the proxy script
echo "Running the proxy script..."
source ./runproxy.sh

