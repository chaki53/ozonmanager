#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Требуется Docker. Установите его и повторите."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "❌ Требуется Docker Compose v2."
  exit 1
fi

if [ ! -f ".env" ]; then
  echo "Создаю .env из .env.sample"
  cp .env.sample .env
fi

echo "🔧 Сборка и запуск контейнеров..."
docker compose up --build -d

echo "🗄  Применяю миграции..."
docker compose exec -T backend alembic upgrade head

echo "👤 Сидирую первого администратора..."
docker compose exec -T backend python - <<'PY'
from app.db.session import SessionLocal
from app.db.seed import seed_first_admin
s=SessionLocal(); seed_first_admin(s); s.close()
PY

echo "✅ Готово! API: http://localhost:8000, Frontend: http://localhost:3000"
