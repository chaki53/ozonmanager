import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class StockSnapshot(Base):
    __tablename__ = "stock_snapshot"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ts = Column(DateTime, nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouse.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False, index=True)
    on_hand = Column(Integer, nullable=False, default=0)
    reserved = Column(Integer, nullable=False, default=0)
    inbound = Column(Integer, nullable=False, default=0)
