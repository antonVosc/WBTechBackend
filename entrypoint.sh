set -e

echo "Ожидаю PostgreSQL ${POSTGRES_HOST:-db} на порту ${POSTGRES_PORT:-5434}..."
until python - <<'PYEOF'
import os
import socket
import sys
import time

host = os.getenv("POSTGRES_HOST", "db")
port = int(os.getenv("POSTGRES_PORT", "5434"))

for _ in range(30):
    try:
        socket.create_connection((host, port), timeout=1).close()

        sys.exit(0)
    except OSError:
        time.sleep(1)

sys.exit(1)
PYEOF

do
  sleep 1
done

echo "PostgreSQL работает."

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000
