"""Compound / CompoundScore / CompoundEvidence / SpeciesAlert. CLAUDE.md: 점수 컬럼은 전부 nullable, 데이터 없음=None."""

from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# SQLite는 INTEGER PRIMARY KEY만 autoincrement한다 (auth_kit/models.py와 동일한 이유).
_PK = BigInteger().with_variant(Integer, "sqlite")


class Compound(Base):
    __tablename__ = "compounds"

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    ingredient_name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class CompoundScore(Base):
    __tablename__ = "compound_scores"
    __table_args__ = (UniqueConstraint("compound_id", "species", name="uq_compound_scores_compound_species"),)

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    compound_id: Mapped[int] = mapped_column(ForeignKey("compounds.id"), nullable=False)
    species: Mapped[str] = mapped_column(String(10), nullable=False)
    # 전부 nullable: 구성요소가 전부 NULL이면 지수 자체도 None (0으로 치환 금지, CLAUDE.md).
    risk_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    opportunity_index: Mapped[float | None] = mapped_column(Float, nullable=True)
    opportunity_coverage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class CompoundEvidence(Base):
    """구성요소(r1~r4/o1~o3)별 근거 카드. value가 None이면 화면에서 회색 처리."""

    __tablename__ = "compound_evidences"
    __table_args__ = (
        UniqueConstraint(
            "compound_id", "species", "component_key", name="uq_compound_evidences_compound_species_component"
        ),
    )

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    compound_id: Mapped[int] = mapped_column(ForeignKey("compounds.id"), nullable=False)
    species: Mapped[str] = mapped_column(String(10), nullable=False)
    component_key: Mapped[str] = mapped_column(String(10), nullable=False)  # r1..r4, o1..o3
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SpeciesAlert(Base):
    """종별 위험 신호 원자료(동물 이상반응 등). CompoundEvidence는 요약 카드, 이쪽은 원본 보관용."""

    __tablename__ = "species_alerts"

    id: Mapped[int] = mapped_column(_PK, primary_key=True, autoincrement=True)
    compound_id: Mapped[int] = mapped_column(ForeignKey("compounds.id"), nullable=False)
    species: Mapped[str] = mapped_column(String(10), nullable=False)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
