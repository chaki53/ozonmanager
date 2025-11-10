import uuid
from sqlalchemy import Column, String, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Product(Base):
    __tablename__ = "product"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("account.id"), nullable=False, index=True)
    sku = Column(BigInteger, nullable=False, index=True)
    name = Column(String, nullable=False)
    barcode = Column(String, nullable=True)
