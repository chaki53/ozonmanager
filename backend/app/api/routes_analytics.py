from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/stock_overview")
def stock_overview(
    account_ids: Optional[List[str]] = Query(None),
    warehouse_ids: Optional[List[str]] = Query(None),
    product_ids: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    sql = text("""WITH last_stock AS (
  SELECT DISTINCT ON (account_id, warehouse_id, product_id)
         account_id, warehouse_id, product_id, ts, on_hand, inbound, reserved
  FROM stock_snapshot
  ORDER BY account_id, warehouse_id, product_id, ts DESC
), doc_calc AS (
  SELECT ls.account_id, ls.warehouse_id, ls.product_id,
         ls.on_hand, ls.inbound, ls.reserved,
         COALESCE(d.dr7,0) AS dr7,
         CASE WHEN COALESCE(d.dr7,0)=0 THEN NULL ELSE ls.on_hand/d.dr7 END AS doc_days
  FROM last_stock ls
  LEFT JOIN dr7_view d
    ON d.account_id=ls.account_id AND d.warehouse_id=ls.warehouse_id AND d.product_id=ls.product_id
)
SELECT * FROM doc_calc
WHERE (:aids IS NULL OR account_id = ANY(:aids))
  AND (:wids IS NULL OR warehouse_id = ANY(:wids))
  AND (:pids IS NULL OR product_id = ANY(:pids));
""")
    params = {
        "aids": account_ids if account_ids else None,
        "wids": warehouse_ids if warehouse_ids else None,
        "pids": product_ids if product_ids else None,
    }
    rows = db.execute(sql, params).fetchall()
    return [dict(r) for r in rows]
