import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class ReportPreference(Base):
    __tablename__ = "report_preference"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    report_key = Column(String, nullable=False)  # e.g., 'sales_summary', 'stock_doc', 'transactions'
    show_on_dashboard = Column(Boolean, nullable=False, server_default="true")
    send_to_telegram = Column(Boolean, nullable=False, server_default="false")
    send_to_email = Column(Boolean, nullable=False, server_default="false")
