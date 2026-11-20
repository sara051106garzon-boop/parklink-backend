# wsgi.py
"""
Punto de entrada para servidores WSGI de producción.

Se usa desde el contenedor:

    gunicorn --worker-class gthread --threads 100 wsgi:app

Gunicorn sirve HTTP normal (Flask); las rutas /socket.io/* las atiende
Flask-SocketIO sobre el mismo puerto, sin necesitar un worker async especial.
"""
from app import create_app

app = create_app()
