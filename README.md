# Ozon Inventory Analytics (MVP)

Готовый каркас: FastAPI + Next.js + PostgreSQL + Redis + Celery.
- **Озон API ключи добавляют только Manager/Admin** (RBAC).
- **Панель и админ‑панель доступны извне** (порты 3000 и 8000 опубликованы). Рекомендуется поставить nginx перед приложением в проде.
- Автосоздание администратора, авто‑синхронизация (Celery Beat), принудительная синхронизация, отчёты в TG и на e‑mail (PDF).

## Быстрый старт
```bash
cp .env.sample .env
./install.sh
```
- Frontend: http://localhost:3000 (вкл. `/admin`)
- API: http://localhost:8000 (JWT авторизация)

### Логин
`admin@local` / `admin123` (сразу смените)

## RBAC
- Добавление/изменение Ozon API аккаунтов — **Manager+** (`POST /accounts`)
- Удаление аккаунтов — **Admin** (`DELETE /accounts/{id}`)
- Принудительная синхронизация — **Manager+** (`POST /sync/run`)

## Принудительный синк
```bash
./sync.sh
# или через API с Bearer токеном:
curl -X POST http://localhost:8000/sync/run -H "Authorization: Bearer <token>"
```

## Автосинхронизация
Celery Beat с интервалами из `.env`: `SYNC_PERIOD_SECONDS`, `DAILY_REPORT_SECONDS`.
