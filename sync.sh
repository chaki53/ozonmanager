#!/usr/bin/env bash
set -euo pipefail
echo "▶️ Принудительная синхронизация всех аккаунтов..."
docker compose exec -T backend python -m app.services.sync --force
echo "✅ Синхронизация завершена."
