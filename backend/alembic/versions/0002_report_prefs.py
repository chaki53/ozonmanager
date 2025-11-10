from alembic import op
import sqlalchemy as sa

revision = "0002_report_prefs"
down_revision = "0001_init"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "report_preference",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("report_key", sa.String(), nullable=False),
        sa.Column("show_on_dashboard", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("send_to_telegram", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("send_to_email", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

def downgrade():
    op.drop_table("report_preference")
