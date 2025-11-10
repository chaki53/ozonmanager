from typing import List, Dict

# Каталог доступных отчётов (ключ, название, описание)
REPORTS: List[Dict] = [
    {"key": "sales_summary", "title": "Продажи: сводка", "description": "Выручка, заказы, средний чек"},
    {"key": "stock_doc", "title": "Запасы и Days of Cover", "description": "Остатки, расход, DoC"},
    {"key": "abcxyz", "title": "ABC/XYZ", "description": "Классификация по обороту и стабильности"},
    {"key": "transactions", "title": "Финансовые транзакции", "description": "Начисления, комиссии, выплаты"},
    {"key": "postings", "title": "Отгрузки (FBO/FBS)", "description": "Статусы, SLA, проблемные позиции"},
]

def list_reports() -> List[Dict]:
    return REPORTS

def exists(key: str) -> bool:
    return any(r["key"] == key for r in REPORTS)
