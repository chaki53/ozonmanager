# Ozon Inventory Analytics (MVP) — Ingest-only

Эта сборка настроена **односторонне**: данные **тянутся из Ozon → в вашу панель**.
- Ключ `OZON_READONLY=true` запрещает любые неразрешённые вызовы к API Ozon.
- Клиент `OzonClient` имеет **белый список** только читающих эндпоинтов.
- Синхронизация **никогда не пишет** что-либо в Ozon API — только читает и сохраняет локально.

## Быстрый старт
```bash
cp .env.sample .env
./install.sh
```

## Принудительная синхронизация
```bash
./sync.sh
# или POST https://api.<домена>/sync/run (JWT: Manager/Admin)
```
