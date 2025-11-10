import httpx
from typing import Any, Dict, List, Optional
from app.core.config import settings

READ_ENDPOINTS = {
    "/v1/warehouse/list": "POST",
    "/v2/warehouse/list": "POST",
    "/v2/product/list": "POST",
    "/v3/product/info/list": "POST",
    "/v1/analytics/data": "POST",
    "/v2/analytics/stock_on_warehouses": "POST",
    "/v2/posting/fbo/list": "POST",
    "/v3/posting/fbs/list": "POST",
    "/v3/posting/fbo/list": "POST",
}

class OzonClient:
    def __init__(self, client_id: str, api_key: str):
        self._base = settings.OZON_BASE_URL.rstrip("/")
        self.client = httpx.Client(
            base_url=self._base,
            headers={"Client-Id": client_id, "Api-Key": api_key, "Content-Type": "application/json"},
            timeout=60,
        )

    def _call(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if path not in READ_ENDPOINTS and settings.OZON_READONLY:
            raise RuntimeError(f"OZON_READONLY blocks {path}")
        method = READ_ENDPOINTS.get(path, "POST")
        r = self.client.request(method, path, json=payload or {})
        r.raise_for_status()
        return r.json()

    # Warehouses
    def list_warehouses(self) -> List[Dict[str, Any]]:
        data = self._call("/v1/warehouse/list", {})
        # normalize
        return data.get("result", []) or data.get("warehouses", []) or []

    # Products (paged)
    def iter_products(self, page_size: int = 100):
        page = 1
        while True:
            data = self._call("/v2/product/list", {"page": page, "page_size": page_size})
            items = (data.get("result") or {}).get("items") or []
            if not items:
                break
            yield from items
            if len(items) < page_size:
                break
            page += 1

    # Stock by warehouses (batch by sku)
    def stock_on_warehouses(self, skus: List[int]) -> Dict[str, Any]:
        return self._call("/v2/analytics/stock_on_warehouses", {"sku": skus})

    # Sales via analytics/data (ordered_units) date range
    def analytics_units(self, date_from: str, date_to: str, dimension: str = "day") -> Dict[str, Any]:
        return self._call("/v1/analytics/data", {
            "date_from": date_from,
            "date_to": date_to,
            "metrics": ["ordered_units"],
            "dimension": [dimension],
        })

    # Postings FBO/FBS (optional alternative)
    def postings_fbs(self, date_from: str, date_to: str, limit: int = 1000) -> Dict[str, Any]:
        return self._call("/v3/posting/fbs/list", {"filter": {"date_from": date_from, "date_to": date_to}, "limit": limit})

    def postings_fbo(self, date_from: str, date_to: str, limit: int = 1000) -> Dict[str, Any]:
        return self._call("/v3/posting/fbo/list", {"filter": {"date_from": date_from, "date_to": date_to}, "limit": limit})
