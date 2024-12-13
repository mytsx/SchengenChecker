#!/bin/bash

python3 checker_runner.py   & 

gunicorn -w 4 -b 0.0.0.0:8080 app:flask_app  
