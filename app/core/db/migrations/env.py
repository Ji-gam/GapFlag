import asyncio
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import create_async_engine

import app.models  # noqa: F401  # 모델을 Base.metadata에 등록하기 위한 임포트
from app.core import config as app_config
from app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# 접속 대상은 app/core/db/databases.py와 같은 값(config.DATABASE_URL)을 쓴다.
# 두 곳에 URL을 각각 하드코딩하면 로컬/배포 전환 때 한쪽만 바뀌는 사고가 난다.
DATABASE_URL = app_config.DATABASE_URL
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# SQLite는 ALTER TABLE 지원이 제한적이라, Alembic이 임시 테이블을 만들어 옮기는
# batch 모드가 필요하다(render_as_batch). MySQL에서는 켜도 동작에 영향이 없다.
RENDER_AS_BATCH = IS_SQLITE


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=RENDER_AS_BATCH,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=RENDER_AS_BATCH,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    if IS_SQLITE:
        # SQLite 파일이 놓일 디렉터리를 미리 만든다(없으면 접속 시점에 실패한다).
        db_path = DATABASE_URL.split("///", 1)[-1]
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    connectable = create_async_engine(DATABASE_URL)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
