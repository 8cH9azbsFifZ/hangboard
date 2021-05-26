#!/bin/bash
python3 -m venv venv
source venv/bin/activate
python3 exercise.py --host 127.0.0.1 --port 9090 --portrecv 9091