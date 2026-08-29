from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import config

# 접속 대상은 config.DATABASE_URL 하나로 결정된다.
#   로컬 개발 : sqlite+aiosqlite:///./data/gapflag.db  (기본값 — MySQL 설치 불필요)
#   배포/검증 : mysql+asyncmy://USER:PASSWORD@HOST:PORT/NAME
# 두 경우 모두 비동기 드라이버라서, Repository 계층 코드는 어느 쪽이든 동일하다.
DATABASE_URL = config.DATABASE_URL
IS_SQLITE = DATABASE_URL.startswith("sqlite")

if IS_SQLITE:
    # SQLite 파일이 놓일 디렉터리를 미리 만든다(없으면 접속 시점에 실패한다).
    db_path = DATABASE_URL.split("///", 1)[-1]
    if db_path and db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    # aiosqlite는 pool_size / connect_timeout 옵션을 받지 않으므로 기본값으로 만든다.
    engine = create_async_engine(DATABASE_URL)
else:
    engine = create_async_engine(
        DATABASE_URL,
        pool_size=config.DB_CONNECTION_POOL_MAXSIZE,
        connect_args={"connect_timeout": config.DB_CONNECT_TIMEOUT},
    )

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
