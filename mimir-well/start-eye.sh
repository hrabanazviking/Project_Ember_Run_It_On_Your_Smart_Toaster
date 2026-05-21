#!/bin/bash
# Mímir's Eye Launcher
# Sets PYTHONPATH and starts the Flask dashboard
export PYTHONPATH="/home/pi/.local/lib/python3.11/site-packages:/home/pi/mimir-well/src:$PYTHONPATH"
cd /home/pi/mimir-well
exec /usr/bin/python3 -c "from mimir_well.eye.app import main; main()" "$@"