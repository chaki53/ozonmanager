from app.db.session import get_db_session
from app.models.account import Account
from app.services.ozon_client import OzonClient
from app.services.analytics import upsert_sales, upsert_stocks
from app.core.config import settings
import argparse

def _sync_all():
    with get_db_session() as db:
        accounts = db.query(Account).all()
        for acc in accounts:
            client = OzonClient(acc.ozon_client_id, acc.ozon_api_key_enc)  # ENC заглушка
            upsert_stocks(db, acc, client)
            upsert_sales(db, acc, client)

def force_sync_all():
    _sync_all()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force sync now")
    args = parser.parse_args()
    if args.force:
        force_sync_all()
    else:
        force_sync_all()

if __name__ == "__main__":
    main()
