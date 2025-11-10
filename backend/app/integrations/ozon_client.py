import httpx
from typing import Any, Dict, Optional, List
from datetime import datetime

OZON_BASE_URL = "https://api-seller.ozon.ru"

class OzonClient:
    def __init__(self, client_id: str, api_key: str, base_url: str = OZON_BASE_URL, timeout: float = 30.0):
        self.client_id = client_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:
        return {
            "Client-Id": self.client_id,
            "Api-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def health(self) -> bool:
        # лёгкая проверка: дернуть нестрогий метод (можно заменить на products/list)
        try:
            with httpx.Client(timeout=self.timeout) as c:
                r = c.post(f"{self.base_url}/v3/product/info/attributes", headers=self._headers(), json={"filter": {"offer_id": []}, "last_id": ""})
            return r.status_code in (200,400,404)  # заголовки/подпись ок
        except Exception:
            return False

    def analytics_data(self, date_from: str, date_to: str, dimensions: List[str], metrics: List[str], limit: int = 1000, last_id: str = "") -> Dict[str, Any]:
        payload = {
            "date_from": date_from,
            "date_to": date_to,
            "dimension": dimensions,
            "metrics": metrics,
            "limit": limit,
        }
        if last_id:
            payload["last_id"] = last_id
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(f"{self.base_url}/v3/analytics/data", headers=self._headers(), json=payload)
            r.raise_for_status()
            return r.json()

    # Заготовки под остатки/склады/постинги — дополним по нужным эндпойнтам:
    def list_products(self, last_id: str = "", limit: int = 1000) -> Dict[str, Any]:
        payload = {"filter": {}, "last_id": last_id, "limit": limit}
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(f"{self.base_url}/v3/product/list", headers=self._headers(), json=payload)
            r.raise_for_status()
            return r.json()
