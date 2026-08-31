"""Compound 조회 조합. Repository 결과를 화면 템플릿이 쓰는 dict 모양으로 조립한다."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import cmp_repository

_LABELS = {
    "r1": "임상 중단 이력",
    "r2": "동물 이상반응",
    "r3": "승인·철회 이력",
    "r4": "특허 밀집도",
    "o1": "문헌 희소성",
    "o2": "임상 부재",
    "o3": "미승인 여부",
}
_RISK_KEYS = ("r1", "r2", "r3", "r4")
_OPPORTUNITY_KEYS = ("o1", "o2", "o3")


async def search_compounds(db: AsyncSession, query: str) -> list[dict]:
    pairs = await cmp_repository.search_compound_species(db, query)
    return [{"ingredient_name": name, "species": species} for name, species in pairs]


async def get_compound_view(db: AsyncSession, ingredient_name: str, species: str) -> dict | None:
    """DB에 저장된 성분·종 조합만 반환. 지수는 build_cache.py가 미리 계산해둔 값을 그대로 읽는다
    (CLAUDE.md: 화면은 DB만 읽는다 — 여기서 재계산하지 않는다)."""
    compound = await cmp_repository.get_compound_by_name(db, ingredient_name)
    if compound is None:
        return None
    score = await cmp_repository.get_score(db, compound.id, species)
    if score is None:
        return None

    evidences = {e.component_key: e for e in await cmp_repository.get_evidences(db, compound.id, species)}

    def _card(key: str) -> dict:
        e = evidences.get(key)
        return {
            "value": e.value if e else None,
            "label": _LABELS[key],
            "source_name": e.source_name if e else None,
            "summary": e.summary if e else None,
            "source_url": e.source_url if e else None,
        }

    return {
        "ingredient_name": compound.ingredient_name,
        "species": species,
        "risk": {k: _card(k) for k in _RISK_KEYS},
        "opportunity": {k: _card(k) for k in _OPPORTUNITY_KEYS},
        "score": {
            "risk_index": score.risk_index,
            "risk_coverage": score.risk_coverage,
            "opportunity_index": score.opportunity_index,
            "opportunity_coverage": score.opportunity_coverage,
        },
    }
