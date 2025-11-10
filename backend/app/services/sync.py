from app.db.session import get_db_session
from app.models.account import Account
from app.services.ozon_client import OzonClient
from app.core.config import settings
import argparse

def _sync_account(acc):
    client = OzonClient(acc.ozon_client_id, acc.ozon_api_key_enc)  # ENC заглушка
    # Примеры чтения
    wh = client.list_warehouses()
    products = client.list_products(page=1, page_size=100)
    # TODO: сохранить в локальную БД (таблицы справочников и снапшоты остатков/продаж)
    # Здесь НЕТ обратной записи в Ozon — только загрузка в нашу систему.

def _sync_all():
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        accounts = db.query(Account).all()
        for acc in accounts:
            _sync_account(acc)
    finally:
        db.close()

def force_sync_all():
    _sync_all()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    force_sync_all()

if __name__ == "__main__":
    main()
