# Диапазон дат (from/to)

- Для дашборда доступны эндпоинты:
  - `GET /dashboard/kpi?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`
  - `GET /dashboard/widgets?report_key=<key>&date_from=YYYY-MM-DD&date_to=YYYY-MM-DD`
- На фронте `/dashboard` добавлены поля выбора дат «С» и «По» — период применяется ко всем виджетам.
- В `/reports/send` и `/reports/render/{report_key}` передавайте диапазон в `params`:
  ```json
  {
    "report_keys": ["sales_summary"],
    "params": { "date_from": "2025-10-01", "date_to": "2025-11-10" }
  }
  ```
