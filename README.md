# Интеграция Ozon (ingest-only) и синк

### Синк по выбранным аккаунтам и глубине продаж
```bash
curl -X POST https://api.<домен>/sync/run \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{ "account_ids": ["<uuid>", "<uuid>"], "sales_days": 30 }'
```

### Telegram chat id (персонально)
```bash
curl -X POST https://api.<домен>/me/telegram \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{ "telegram_chat_id": "123456789" }'
```

> Продажи per SKU/склад для точного DR/DoC лучше считать по postings (FBO/FBS). В MVP заложены каркасы; можно оперативно добавить агрегирование из отгрузок.
