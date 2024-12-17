#!/bin/bash

echo "Şemalar senkronize ediliyor, veriler aktarılıyor..."
python3 sync_database.py &

echo "Checker runner başlatılıyor..."
python3 checker_runner.py &

echo "Flask uygulaması başlatılıyor..."
gunicorn -w 4 -b 0.0.0.0:8080 app:flask_app
