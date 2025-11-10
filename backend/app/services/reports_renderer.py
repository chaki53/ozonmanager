from typing import Dict, Any, List
from app.services.pdf import render_pdf

def render_html(report_key: str, params: Dict[str, Any]) -> str:
    # TODO: Реализовать реальные выборки и графики.
    title = {
        "sales_summary": "Продажи: сводка",
        "stock_doc": "Запасы и DoC",
        "abcxyz": "ABC/XYZ",
        "transactions": "Финансовые транзакции",
        "postings": "Отгрузки (FBO/FBS)",
    }.get(report_key, report_key)
    return f"""
    <html><body>
      <h1>{title}</h1>
      <p>Параметры: {params}</p>
      <div>Данные будут подтянуты из БД и Ozon API (ingest-only)</div>
    </body></html>
    """

def render_pdf_bytes(report_key: str, params: Dict[str, Any]) -> bytes:
    html = render_html(report_key, params)
    path = "/tmp/_report_tmp.pdf"
    render_pdf(html, path)
    with open(path, "rb") as f:
        return f.read()

def bundle_pdf_bytes(keys: List[str], params: Dict[str, Any]) -> Dict[str, bytes]:
    return {f"{k}.pdf": render_pdf_bytes(k, params) for k in keys}
