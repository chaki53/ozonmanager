import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Account(Base):
    __tablename__ = "account"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ozon_client_id = Column(Text, nullable=False)
    ozon_api_key_enc = Column(Text, nullable=False)
    tz = Column(String, default="Europe/Moscow")
