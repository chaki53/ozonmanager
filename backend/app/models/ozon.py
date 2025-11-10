from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.base import Base

def utcnow():
    return datetime.now(timezone.utc)

class OzonAccount(Base):
    __tablename__ = "ozon_account"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    api_key = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)

class Warehouse(Base):
    __tablename__ = "warehouse"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("ozon_account.id"), nullable=False, index=True)
    wh_id = Column(Integer, nullable=False)  # ozon warehouse id
    name = Column(String, nullable=False)
    __table_args__ = (UniqueConstraint('account_id','wh_id', name='uq_wh_account_whid'),)

class AnalyticsDaily(Base):
    __tablename__ = "analytics_daily"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("ozon_account.id"), index=True, nullable=False)
    day = Column(DateTime(timezone=True), index=True, nullable=False)
    sku = Column(Integer, index=True, nullable=True)
    offer_id = Column(String, index=True, nullable=True)
    revenue = Column(Float, default=0)
    ordered_units = Column(Integer, default=0)
    returns = Column(Integer, default=0)
    views = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('account_id','day','sku','offer_id', name='uq_analytics_key'),)

class StockDaily(Base):
    __tablename__ = "stock_daily"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("ozon_account.id"), index=True, nullable=False)
    day = Column(DateTime(timezone=True), index=True, nullable=False)
    warehouse_id = Column(Integer, index=True, nullable=True)  # ozon wh id
    sku = Column(Integer, index=True, nullable=True)
    offer_id = Column(String, index=True, nullable=True)
    stock = Column(Integer, default=0)
    in_transit = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('account_id','day','warehouse_id','sku','offer_id', name='uq_stock_key'),)

class SalesDaily(Base):
    __tablename__ = "sales_daily"
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("ozon_account.id"), index=True, nullable=False)
    day = Column(DateTime(timezone=True), index=True, nullable=False)
    sku = Column(Integer, index=True, nullable=True)
    offer_id = Column(String, index=True, nullable=True)
    sold_units = Column(Integer, default=0)
    __table_args__ = (UniqueConstraint('account_id','day','sku','offer_id', name='uq_sales_key'),)
