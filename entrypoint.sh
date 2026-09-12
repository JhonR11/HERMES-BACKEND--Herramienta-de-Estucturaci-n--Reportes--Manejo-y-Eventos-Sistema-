#!/bin/sh
set -e
echo "Esperando PostgreSQL..."
python - <<'PY'
import socket, time, os
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"No se pudo conectar a {host}:{port}")
PY
echo "Aplicando migraciones..."
alembic upgrade head
echo "Ejecutando seed de administrador..."
python -m app.infrastructure.db.seed
echo "Arrancando API..."
exec uvicorn app.presentation.main:app --host 0.0.0.0 --port 8000
