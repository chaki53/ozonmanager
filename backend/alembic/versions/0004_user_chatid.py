from alembic import op
import sqlalchemy as sa

revision = "0004_user_chatid"
down_revision = "0003_inventory_sales"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("user", sa.Column("telegram_chat_id", sa.String(), nullable=True))

def downgrade():
    op.drop_column("user", "telegram_chat_id")
