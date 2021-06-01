#!/bin/bash
python3 -m venv venv
source venv/bin/activate

python3 exercises.py --host 127.0.0.1 --port 4321

