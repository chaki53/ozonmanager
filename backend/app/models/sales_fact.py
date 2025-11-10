import uuid
from sqlalchemy import Column, Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class SalesFact(Base):
    __tablename__ = "sales_fact"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dt = Column(Date, nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouse.id"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("product.id"), nullable=False, index=True)
    qty = Column(Integer, nullable=False, default=0)
