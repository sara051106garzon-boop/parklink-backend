FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# La app escucha en 5000 dentro del contenedor; el puerto público se mapea
# con APP_PORT en docker-compose.yml.
ENV APP_PORT=5000

WORKDIR /app

# Dependencias del sistema requeridas para mysqlclient (MySQL/MariaDB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del backend
COPY . .

# Usuario sin privilegios: si la app se viera comprometida, no corre como root.
RUN useradd --create-home --uid 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Servidor WSGI de producción. gthread + gevent monkeado permite muchos
# WebSockets simultáneos sin worker async propietario (se puede escalar con
# --workers según la memoria de la instancia, p. ej. 2-4).
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=4)"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", \
     "--worker-class", "gthread", "--workers", "2", "--threads", "100", \
     "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", \
     "wsgi:app"]
