from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional
from app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/widgets")
def widgets(report_key: str,
            date_from: Optional[date] = Query(None),
            date_to: Optional[date] = Query(None),
            user=Depends(get_current_user)):
    # TODO: Подставить реальные выборки из БД по report_key и диапазону дат
    return {
        "report_key": report_key,
        "date_from": str(date_from) if date_from else None,
        "date_to": str(date_to) if date_to else None,
        "data": {"status": "demo", "points": 42}
    }

@router.get("/kpi")
def kpi(date_from: Optional[date] = Query(None),
        date_to: Optional[date] = Query(None),
        user=Depends(get_current_user)):
    # TODO: Вернуть агрегированные KPI за период
    return {
        "date_from": str(date_from) if date_from else None,
        "date_to": str(date_to) if date_to else None,
        "kpi": {"revenue": 100000, "orders": 123, "avg_check": 813.01}
    }
