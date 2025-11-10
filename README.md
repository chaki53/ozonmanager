# Ozon Inventory Analytics (MVP)

FastAPI + Next.js + PostgreSQL + Redis + Celery + Telegram + PDF.
- RBAC: Ozon API добавляют **Manager/Admin**.
- Дашборд и админка доступны извне через **Nginx + Let's Encrypt** (автонастройка в `install.sh`).

## Быстрый старт
```bash
cp .env.sample .env
./install.sh
```
Инсталлятор:
1. Поднимет Docker‑стек (службы привязаны к 127.0.0.1).
2. Применит миграции и создаст первого админа.
3. Предложит установить **Nginx** и выпустить **SSL-сертификаты** (ввод домена и e‑mail).
   - Frontend → https://<ваш_домен>
   - API → https://api.<ваш_домен>

## Ручной синк
```bash
./sync.sh
```

## Автосинхронизация
Celery Beat с интервалами `SYNC_PERIOD_SECONDS`, `DAILY_REPORT_SECONDS` из `.env`.
