"""매트릭스 산점도용 cmp_service.list_matrix_points: NULL 지수 조합도 빠지지 않는지 확인."""

from collections.abc import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base
from app.repositories import cmp_repository
from app.services import cmp_service


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_local = async_sessionmaker(engine, expire_on_commit=False)
    async with session_local() as session:
        yield session
    await engine.dispose()


async def test_list_matrix_points_keeps_null_index_compounds(db: AsyncSession) -> None:
    full = await cmp_repository.upsert_compound(db, "carprofen")
    await cmp_repository.upsert_score(
        db, full.id, "dog", risk_index=45.0, risk_coverage=1.0, opportunity_index=60.0, opportunity_coverage=1.0
    )
    partial = await cmp_repository.upsert_compound(db, "gabapentin")
    await cmp_repository.upsert_score(
        db, partial.id, "cat", risk_index=None, risk_coverage=0.0, opportunity_index=80.0, opportunity_coverage=0.5
    )
    await db.commit()

    points = await cmp_service.list_matrix_points(db)

    assert len(points) == 2
    by_name = {p["ingredient_name"]: p for p in points}
    assert by_name["carprofen"]["risk_index"] == 45.0
    assert by_name["gabapentin"]["risk_index"] is None  # 데이터 없음은 None, 0으로 치환하지 않는다
    assert by_name["gabapentin"]["opportunity_index"] == 80.0
