from alembic import op
import sqlalchemy as sa
import uuid

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.create_table(
        "user",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_table(
        "account",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("ozon_client_id", sa.Text(), nullable=False),
        sa.Column("ozon_api_key_enc", sa.Text(), nullable=False),
        sa.Column("tz", sa.String(), nullable=False, server_default="Europe/Moscow"),
    )

def downgrade():
    op.drop_table("account")
    op.drop_table("user")
