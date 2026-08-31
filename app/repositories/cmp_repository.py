"""Compound 관련 쿼리만 (AsyncSession + select(), CLAUDE.md: session.query() 금지)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cmp_models import Compound, CompoundEvidence, CompoundScore


async def get_compound_by_name(db: AsyncSession, ingredient_name: str) -> Compound | None:
    stmt = select(Compound).where(Compound.ingredient_name == ingredient_name.strip().lower())
    return (await db.execute(stmt)).scalar_one_or_none()


async def search_compounds(db: AsyncSession, query: str) -> list[Compound]:
    stmt = select(Compound)
    q = query.strip().lower()
    if q:
        stmt = stmt.where(Compound.ingredient_name.contains(q))
    return list((await db.execute(stmt)).scalars())


async def get_score(db: AsyncSession, compound_id: int, species: str) -> CompoundScore | None:
    stmt = select(CompoundScore).where(CompoundScore.compound_id == compound_id, CompoundScore.species == species)
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_evidences(db: AsyncSession, compound_id: int, species: str) -> list[CompoundEvidence]:
    stmt = select(CompoundEvidence).where(
        CompoundEvidence.compound_id == compound_id, CompoundEvidence.species == species
    )
    return list((await db.execute(stmt)).scalars())


async def upsert_compound(db: AsyncSession, ingredient_name: str) -> Compound:
    name = ingredient_name.strip().lower()
    compound = await get_compound_by_name(db, name)
    if compound is None:
        compound = Compound(ingredient_name=name)
        db.add(compound)
        await db.flush()
    return compound


async def upsert_evidence(
    db: AsyncSession,
    compound_id: int,
    species: str,
    component_key: str,
    *,
    value: float | None,
    source_name: str | None,
    summary: str | None,
    source_url: str | None,
    raw_json: dict | None,
) -> CompoundEvidence:
    stmt = select(CompoundEvidence).where(
        CompoundEvidence.compound_id == compound_id,
        CompoundEvidence.species == species,
        CompoundEvidence.component_key == component_key,
    )
    evidence = (await db.execute(stmt)).scalar_one_or_none()
    if evidence is None:
        evidence = CompoundEvidence(compound_id=compound_id, species=species, component_key=component_key)
        db.add(evidence)
    evidence.value = value
    evidence.source_name = source_name
    evidence.summary = summary
    evidence.source_url = source_url
    evidence.raw_json = raw_json
    return evidence


async def upsert_score(
    db: AsyncSession,
    compound_id: int,
    species: str,
    *,
    risk_index: float | None,
    risk_coverage: float,
    opportunity_index: float | None,
    opportunity_coverage: float,
) -> CompoundScore:
    score = await get_score(db, compound_id, species)
    if score is None:
        score = CompoundScore(compound_id=compound_id, species=species)
        db.add(score)
    score.risk_index = risk_index
    score.risk_coverage = risk_coverage
    score.opportunity_index = opportunity_index
    score.opportunity_coverage = opportunity_coverage
    return score
