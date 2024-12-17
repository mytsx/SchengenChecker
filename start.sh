#!/bin/bash


# 3. Ana uygulamayı başlat
echo "Checker runner başlatılıyor..."
python3 checker_runner.py &

echo "Flask uygulaması başlatılıyor..."
gunicorn -w 4 -b 0.0.0.0:8080 app:flask_app
