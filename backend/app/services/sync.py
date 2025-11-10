from datetime import date, timedelta
from app.db.session import get_db_session
from app.models.account import Account
from app.services.ozon_client import OzonClient
from app.services.ingest import upsert_warehouses, upsert_products, upsert_stock_snapshots, upsert_sales_daily, refresh_dr7

def sync_accounts(account_ids=None, sales_days: int = 14):
    with get_db_session() as db:
        q = db.query(Account)
        if account_ids:
            q = q.filter(Account.id.in_(account_ids))
        accounts = q.all()
        for acc in accounts:
            client = OzonClient(acc.ozon_client_id, acc.ozon_api_key_enc)  # ENC заглушка
            upsert_warehouses(db, acc, client)
            upsert_products(db, acc, client)
            upsert_stock_snapshots(db, acc, client)
            # sales by postings is preferred; analytics_units kept for totals. For MVP, skip per-SKU sales until postings logic is added.
            date_to = date.today()
            date_from = date_to - timedelta(days=sales_days)
            upsert_sales_daily(db, acc, client, date_from, date_to)
        refresh_dr7(db)
        db.commit()

def force_sync_all():
    sync_accounts()

if __name__ == "__main__":
    force_sync_all()
