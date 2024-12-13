#!/bin/bash

# Start the Flask app in the background
python3 app.py &

# Start the SchengenChecker script
python3 SchengenChecker.py
