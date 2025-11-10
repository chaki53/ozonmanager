from fastapi import APIRouter, Query, Depends
from app.core.security import get_current_user

router = APIRouter(tags=["search"])

@router.get("/search")
def search(q: str, user=Depends(get_current_user)):
    # TODO: заменить на реальный поиск в БД по SKU / имени / offer_id
    items = [
        {"sku": 1001, "name": "Товар 1", "offer_id": "A-001"},
        {"sku": 1002, "name": "Товар 2", "offer_id": "B-002"},
    ]
    res = [i for i in items if q.lower() in i["name"].lower() or q in str(i["sku"]) or q.lower() in i["offer_id"].lower()]
    return {"items": res[:10]}
