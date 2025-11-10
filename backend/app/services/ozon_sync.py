from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.ozon import OzonAccount, AnalyticsDaily, StockDaily, SalesDaily
from app.integrations.ozon_client import OzonClient

def to_date(s: str) -> datetime:
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc) if 'T' not in s else datetime.fromisoformat(s)

def sync_analytics(db: Session, account: OzonAccount, date_from: str, date_to: str) -> int:
    client = OzonClient(account.client_id, account.api_key)
    dims = ["day","sku"]  # можно расширять (warehouse, item)
    metrics = ["revenue","ordered_units","returns","session_view"]  # пример
    last_id = ""
    inserted = 0
    while True:
        data = client.analytics_data(date_from, date_to, dims, metrics, limit=1000, last_id=last_id)
        rows = data.get("result", {}).get("data", []) or data.get("result", []) or []
        for row in rows:
            dim = row.get("dimensions", {})
            met = row.get("metrics", {})
            day = dim.get("day") or dim.get("date")
            sku = dim.get("sku")
            offer_id = dim.get("offer_id")
            ad = AnalyticsDaily(
                account_id=account.id,
                day=to_date(day) if isinstance(day,str) else day,
                sku=int(sku) if sku not in (None,"") else None,
                offer_id=offer_id,
                revenue=float(met.get("revenue",0) or 0),
                ordered_units=int(met.get("ordered_units",0) or 0),
                returns=int(met.get("returns",0) or 0),
                views=int(met.get("session_view",0) or 0),
            )
            db.merge(ad)
            inserted += 1
        last_id = (data.get("result", {}) or {}).get("last_id","")
        if not last_id:
            break
    account.last_sync_at = datetime.now(timezone.utc)
    db.add(account); db.commit()
    return inserted
