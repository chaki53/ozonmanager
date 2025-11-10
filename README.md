# Аналитический кабинет и мониторинг (полный набор)

В этом обновлении:
- Модели: `warehouse`, `product`, `stock_snapshot`, `sales_fact`.
- Миграция: `0003_inventory_sales`.
- Материализованный вид `dr7_view` (средний дневной расход 7 дней) и расчёт DoC.
- API: `/analytics/stock_overview` (фильтры по account_ids/warehouse_ids/product_ids).
- Celery‑алерты: проверка DoC < 15 и отправка в Telegram.
- Фронт: `/dashboard/stock` — обзор остатков/скорости/покрытия.

> После ingestion добавьте периодическое `REFRESH MATERIALIZED VIEW CONCURRENTLY dr7_view;` (в Celery или после загрузки продаж) для актуальности DR7.
