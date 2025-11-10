from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os, sys

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Make app models importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.base import Base
from app.models.user import User
from app.models.account import Account
from app.core.config import settings

def run_migrations_offline():
    url = settings.SQLALCHEMY_DATABASE_URI
    context.configure(
        url=str(url),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    conf = config.get_section(config.config_ini_section)
    conf["sqlalchemy.url"] = str(settings.SQLALCHEMY_DATABASE_URI)
    connectable = engine_from_config(conf, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
