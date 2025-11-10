from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.models.report_preference import ReportPreference
from app.services.reports_catalog import list_reports, exists
from app.services.reports_renderer import render_pdf_bytes, bundle_pdf_bytes
from app.services.emailer import send_email
from app.services.telegram_bot import send_alert as send_tg  # reuse stub

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/catalog")
def catalog():
    return list_reports()

@router.get("/preferences")
def get_prefs(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    rows = db.query(ReportPreference).filter(ReportPreference.user_id == user.id).all()
    return [{
        "id": str(r.id),
        "report_key": r.report_key,
        "show_on_dashboard": r.show_on_dashboard,
        "send_to_telegram": r.send_to_telegram,
        "send_to_email": r.send_to_email,
    } for r in rows]

@router.post("/preferences")
def upsert_prefs(payload: List[Dict[str, Any]] = Body(...), db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    # payload: [{report_key, show_on_dashboard, send_to_telegram, send_to_email}]
    for item in payload:
        key = item.get("report_key")
        if not key or not exists(key):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unknown report_key: {key}")
        rec = db.query(ReportPreference).filter(
            ReportPreference.user_id == user.id, ReportPreference.report_key == key
        ).first()
        if not rec:
            rec = ReportPreference(user_id=user.id, report_key=key)
            db.add(rec)
        rec.show_on_dashboard = bool(item.get("show_on_dashboard", False))
        rec.send_to_telegram = bool(item.get("send_to_telegram", False))
        rec.send_to_email = bool(item.get("send_to_email", False))
    db.commit()
    return {"ok": True}

@router.post("/render/{report_key}")
def render_one(report_key: str, params: Dict[str, Any] = Body({}), user=Depends(get_current_user)):
    if not exists(report_key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="report not found")
    pdf = render_pdf_bytes(report_key, params or {})
    return {"ok": True, "bytes": len(pdf)}  # Для MVP не отдаём файл напрямую

@router.post("/send")
def send_reports(payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    # payload: {"report_keys": [...], "email": "...", "telegram_chat_id": "...", "params": {...}}
    keys = payload.get("report_keys") or []
    params = payload.get("params") or {}
    email = payload.get("email")
    chat_id = payload.get("telegram_chat_id")

    for k in keys:
        if not exists(k):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"unknown report_key: {k}")

    bundle = bundle_pdf_bytes(keys, params)

    if email:
        attachments = [(name, data) for name, data in bundle.items()]
        from app.core.config import settings
        html = "<p>Сформированы отчёты: " + ", ".join(keys) + "</p>"
        send_email("Отчёты Ozon", email, html, attachments)

    if chat_id:
        # Для MVP отправим текст с перечислением. В проде: отправка файлов (Telegram sendDocument).
        send_tg({"text": f"Отчёты сформированы: {', '.join(keys)} для параметров {params}", "chat_id": chat_id})

    return {"ok": True}
