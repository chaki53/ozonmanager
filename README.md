# Ozon Inventory Analytics (MVP)

Готовый каркас приложения: FastAPI + Next.js + PostgreSQL + Redis + Celery + Telegram + PDF.
Автосоздание администратора, авто‑синхронизация (Celery Beat), принудительная синхронизация (скрипт/эндпоинт), отчёты в TG и на e‑mail (PDF).

## Быстрый старт
```bash
cp .env.sample .env
./install.sh
```
После установки фронтенд на http://localhost:3000, API на http://localhost:8000.

## Принудительная синхронизация
```bash
./sync.sh
# либо: curl -X POST http://localhost:8000/sync/run -H "Authorization: Bearer <token>"
```

## Роли
- admin — полный доступ
- manager — просмотр, отчёты, запуск синка
- viewer — только чтение
