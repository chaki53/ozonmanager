from alembic import op
import sqlalchemy as sa

revision = "0005_settings"
down_revision = "0004_user_chatid"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "setting",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(), nullable=False, unique=True),
        sa.Column("value", sa.Text(), nullable=False, server_default="")
    )
    op.create_index("ix_setting_key", "setting", ["key"], unique=True)

def downgrade():
    op.drop_table("setting")
