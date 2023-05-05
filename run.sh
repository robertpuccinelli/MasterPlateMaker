#!/bin/bash

# Stop running if any program errors
set -e
shopt -s expand_aliases

# Find absolute path of scripts
curr_path=$PWD
cd ${BASH_SOURCE%/*}
script_path=$PWD
cd ${curr_path}

# Change Python commands for OS
if [[ "$OSTYPE" == "msys" ]]; then
    alias make_venv='python -m venv ${script_path}/venv_mpm'
    alias activate_venv='source ${script_path}/venv_mpm/Scripts/activate'
else
    alias make_venv='python3 -m venv ${script_path}/venv_mpm'
    alias activate_venv='source ${script_path}/venv_mpm/bin/activate'
fi

# Create script to update RSS filter
echo "Checking for program virtual environment"
if ! [ -e ${script_path}/venv_mpm ]
then
    echo "Virtual environment does not exist - creating one now..."
    make_venv
    activate_venv
    echo "Installing wheel"
    pip -q install wheel
    echo "Installing requirements"
    pip -q install -r ${script_path}/requirements.txt
    deactivate
else
    echo "Virtual environment present"
fi

echo "Activating virtual environment and executing program"
activate_venv
python -c 'import MasterPlateMaker as mpm; pgm = mpm.MasterPlateMaker(); pgm.run()'
deactivate

cd ${curr_path}
