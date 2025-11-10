from fastapi import APIRouter
from app.services.pdf import render_pdf
from app.services.emailer import send_email

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/send")
def send_report_stub():
    html = "<h1>Demo Report</h1><p>Это заглушка PDF отчёта.</p>"
    path = "/tmp/report.pdf"
    render_pdf(html, path)
    with open(path, "rb") as f:
        data = f.read()
    send_email("Demo report", "test@example.com", html, [("report.pdf", data)])
    return {"ok": True}
