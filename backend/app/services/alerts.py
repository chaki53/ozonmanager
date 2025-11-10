from sqlalchemy import text
from app.db.session import get_db_session
from app.services.telegram_bot import send_alert

SQL = """
WITH last_stock AS (
  SELECT DISTINCT ON (account_id, warehouse_id, product_id)
         account_id, warehouse_id, product_id, ts, on_hand, inbound, reserved
  FROM stock_snapshot
  ORDER BY account_id, warehouse_id, product_id, ts DESC
), doc_calc AS (
  SELECT ls.account_id, ls.warehouse_id, ls.product_id,
         ls.on_hand, COALESCE(d.dr7,0) AS dr7,
         CASE WHEN COALESCE(d.dr7,0)=0 THEN NULL ELSE ls.on_hand/d.dr7 END AS doc_days
  FROM last_stock ls
  LEFT JOIN dr7_view d
    ON d.account_id=ls.account_id AND d.warehouse_id=ls.warehouse_id AND d.product_id=ls.product_id
)
SELECT * FROM doc_calc WHERE doc_days IS NOT NULL AND doc_days < 15 AND on_hand > 0;
"""

def run_doc_alerts():
    with get_db_session() as db:
        rows = db.execute(text(SQL)).fetchall()
        for r in rows:
            send_alert({
                "text": f"🚨 Меньше 15 дней покрытия\nAcc:{r.account_id} WH:{r.warehouse_id} SKU:{r.product_id}\nOn-hand:{r.on_hand} DR7:{r.dr7:.2f} DoC:{r.doc_days:.1f}"
            })
