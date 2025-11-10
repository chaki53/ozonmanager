from alembic import op
import sqlalchemy as sa

revision = "0003_inventory_sales"
down_revision = "0002_report_prefs"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "warehouse",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ozon_warehouse_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tz", sa.String(), nullable=False, server_default="Europe/Moscow"),
    )
    op.create_index("ix_warehouse_account", "warehouse", ["account_id"])
    op.create_index("ix_warehouse_ozon_id", "warehouse", ["ozon_warehouse_id"])

    op.create_table(
        "product",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sku", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("barcode", sa.String()),
    )
    op.create_index("ix_product_account", "product", ["account_id"])
    op.create_index("ix_product_sku", "product", ["sku"])

    op.create_table(
        "stock_snapshot",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("account_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("on_hand", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inbound", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_stock_ts", "stock_snapshot", ["ts"])
    op.create_index("ix_stock_keys", "stock_snapshot", ["account_id","warehouse_id","product_id"])

    op.create_table(
        "sales_fact",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("dt", sa.Date(), nullable=False),
        sa.Column("account_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_sales_dt", "sales_fact", ["dt"])
    op.create_index("ix_sales_keys", "sales_fact", ["account_id","warehouse_id","product_id"])

def downgrade():
    op.drop_table("sales_fact")
    op.drop_table("stock_snapshot")
    op.drop_table("product")
    op.drop_table("warehouse")
