# run.py
"""
Arranque para DESARROLLO LOCAL (con recarga automática).

En staging/production NO se usa este archivo: el contenedor arranca con
gunicorn (ver Dockerfile / docker-compose.yml) sobre wsgi.py.

    python run.py
"""
import os

from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    # En Docker la app escucha siempre en 5000 (el puerto público lo mapea
    # APP_PORT en docker-compose.yml). En local se puede usar APP_PORT.
    puerto = int(os.getenv("APP_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") in {"1", "true", "True", "yes", "on"}

    socketio.run(app, host="0.0.0.0", port=puerto, debug=debug)
