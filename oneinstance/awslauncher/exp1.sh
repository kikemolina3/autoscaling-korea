#!/bin/bash

set -e
set -x

python3 launch.py --program compilation --duration 600 
python3 launch.py --program encoding --duration 600
python3 launch.py --program compilation --duration 600 --ppcp
python3 launch.py --program encoding --duration 600 --ppcp
