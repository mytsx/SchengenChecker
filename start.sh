
#!/bin/bash
python3 app.py       # Checker scriptini arka planda çalıştır
gunicorn -w 4 -b 0.0.0.0:8080 app:app  # Flask uygulamasını Gunicorn ile çalıştır