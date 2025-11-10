from datetime import datetime, date, timedelta
from typing import Iterable, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.account import Account
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.stock_snapshot import StockSnapshot
from app.models.sales_fact import SalesFact
from app.services.ozon_client import OzonClient
from app.services.analytics_sql import REFRESH_DR7_VIEW

def upsert_warehouses(db: Session, acc: Account, client: OzonClient) -> int:
    data = client.list_warehouses()
    count = 0
    for w in data:
        oz_id = str(w.get("warehouse_id") or w.get("id") or w.get("warehouseId"))
        name = w.get("name") or w.get("warehouse_name") or "Warehouse"
        rec = db.query(Warehouse).filter(Warehouse.account_id==acc.id, Warehouse.ozon_warehouse_id==oz_id).first()
        if not rec:
            rec = Warehouse(account_id=acc.id, ozon_warehouse_id=oz_id, name=name)
            db.add(rec)
            count += 1
        else:
            rec.name = name
    return count

def upsert_products(db: Session, acc: Account, client: OzonClient, page_size: int = 100) -> int:
    count = 0
    for item in client.iter_products(page_size=page_size):
        sku = int(item.get("sku") or item.get("offer_id") or 0)
        if not sku:
            continue
        name = item.get("name") or item.get("title") or f"SKU {sku}"
        rec = db.query(Product).filter(Product.account_id==acc.id, Product.sku==sku).first()
        if not rec:
            rec = Product(account_id=acc.id, sku=sku, name=name)
            db.add(rec); count += 1
        else:
            rec.name = name
    return count

def upsert_stock_snapshots(db: Session, acc: Account, client: OzonClient) -> int:
    # collect all SKUs for account
    skus = [p.sku for p in db.query(Product).filter(Product.account_id==acc.id).all()]
    if not skus:
        return 0
    # Ozon stock endpoint expects list; may need batching if large
    batch = 100
    now_ts = datetime.utcnow()
    inserted = 0
    for i in range(0, len(skus), batch):
        part = skus[i:i+batch]
        res = client.stock_on_warehouses(part)
        # Normalize response
        rows = res.get("result") or res.get("items") or res.get("rows") or []
        for r in rows:
            sku = r.get("sku") or r.get("product_id") or r.get("offer_id")
            wh_id = str(r.get("warehouse_id") or r.get("warehouseId"))
            on_hand = int(r.get("on_hand", r.get("free_to_sell", 0)))
            reserved = int(r.get("reserved", 0))
            inbound = int(r.get("in_transit", 0))
            # Resolve product/warehouse ids
            prod = db.query(Product).filter(Product.account_id==acc.id, Product.sku==int(sku)).first()
            wh = db.query(Warehouse).filter(Warehouse.account_id==acc.id, Warehouse.ozon_warehouse_id==wh_id).first()
            if not prod or not wh:
                continue
            snap = StockSnapshot(
                ts=now_ts, account_id=acc.id, warehouse_id=wh.id, product_id=prod.id,
                on_hand=on_hand, reserved=reserved, inbound=inbound
            )
            db.add(snap); inserted += 1
    return inserted

def upsert_sales_daily(db: Session, acc: Account, client: OzonClient, date_from: date, date_to: date) -> int:
    res = client.analytics_units(date_from.isoformat(), date_to.isoformat(), dimension="day")
    items = res.get("result") or res.get("data") or []
    # Expected format: list of dicts with 'date' and 'metrics' or similar
    inserted = 0
    for it in items:
        # Try common shapes
        dt = it.get("date") or it.get("day") or it.get("dt")
        units = None
        if "ordered_units" in it:
            units = it["ordered_units"]
        elif "metrics" in it and isinstance(it["metrics"], dict):
            units = it["metrics"].get("ordered_units")
        elif "metrics" in it and isinstance(it["metrics"], list) and it["metrics"]:
            units = it["metrics"][0]
        if not dt or units is None:
            continue
        # Distribute by product/warehouse if available — for MVP, aggregate by account and assign to a pseudo-warehouse/product is not ideal.
        # Here we store a single synthetic warehouse/product-less line not supported by schema; instead, skip distribution detail and require postings ingest later.
        # For now, we skip if we cannot map to product/warehouse.
        continue
    # Better: use postings to compute per-warehouse/product daily qty — omitted MVP.
    return inserted

def refresh_dr7(db: Session):
    try:
        db.execute(text(REFRESH_DR7_VIEW))
    except Exception:
        pass
