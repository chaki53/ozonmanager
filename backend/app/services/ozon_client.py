import httpx
from typing import Any, Dict
from app.core.config import settings

# Белый список "читающих" эндпоинтов (POST-методы у Ozon часто читатели)
READ_ENDPOINTS = {
    "/v2/warehouse/list": "POST",
    "/v2/product/list": "POST",
    "/v3/product/info/list": "POST",
    "/v2/analytics/stock_on_warehouses": "POST",
    "/v1/analytics/data": "POST",
    "/v2/finance/transaction/list": "POST",
    "/v2/posting/fbo/list": "POST",
    "/v2/posting/fbs/list": "POST",
    "/v3/posting/fbs/list": "POST",
    "/v3/posting/fbo/list": "POST",
    "/v2/product/info/list": "POST",
    "/v1/warehouse/list": "POST",
}

class OzonClient:
    def __init__(self, client_id: str, api_key: str):
        self._base = settings.OZON_BASE_URL.rstrip("/")
        self._readonly = bool(settings.OZON_READONLY)
        self.client = httpx.Client(
            base_url=self._base,
            headers={"Client-Id": client_id, "Api-Key": api_key, "Content-Type": "application/json"},
            timeout=60,
        )

    def _request_read(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        method = READ_ENDPOINTS.get(path)
        if self._readonly and not method:
            # попытка доступа к неразрешенному эндпоинту
            raise RuntimeError(f"OZON_READONLY: запрещён вызов {path}")
        resp = self.client.request(method or "POST", path, json=payload or {})
        resp.raise_for_status()
        return resp.json()

    # Примеры «только чтение»
    def list_warehouses(self) -> Dict[str, Any]:
        return self._request_read("/v2/warehouse/list", {})

    def list_products(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        return self._request_read("/v2/product/list", {"page": page, "page_size": page_size})

    def stock_on_warehouses(self, sku: list[int] | None = None) -> Dict[str, Any]:
        return self._request_read("/v2/analytics/stock_on_warehouses", {"sku": sku or []})

    def analytics(self, date_from: str, date_to: str, metrics: list[str]) -> Dict[str, Any]:
        return self._request_read("/v1/analytics/data", {
            "date_from": date_from, "date_to": date_to, "metrics": metrics
        })
