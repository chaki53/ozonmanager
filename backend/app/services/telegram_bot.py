import requests
from app.core.config import settings

def send_message(chat_id: str, text: str):
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return
    API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
    try:
        requests.post(f"{API}/sendMessage", json={"chat_id": chat_id, "text": text})
    except Exception:
        pass

def send_alert(payload):
    # payload may include chat_id; otherwise skip
    chat_id = payload.get("chat_id")
    text = payload.get("text", "Alert")
    send_message(chat_id, text)
