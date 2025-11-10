import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Warehouse(Base):
    __tablename__ = "warehouse"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False, index=True)
    ozon_warehouse_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    tz = Column(String, default="Europe/Moscow")
