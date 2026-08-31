"""외부 API에서 성분 데이터를 수집해 DB에 저장 (수동 실행, CLAUDE.md: 화면은 DB만 읽는다).

현재 R1(Open Targets)·R2(openFDA)·R3(Green Book)·O1(Europe PMC)만 실제로 수집한다.
R4·O2·O3는 수집 서비스가 아직 없어 NULL로 남는다(Tier2 stub, CLAUDE.md §11) — 산식이
NULL을 견디도록 설계돼 있어 나중에 서비스를 추가해도 이 스크립트의 계산 로직은 바뀌지 않는다.

대상 성분 30~50건 목록이 아직 확정 전이라(docs/REQUIREMENTS §7-3) SEED_COMPOUNDS에
임시로 몇 개만 넣어둔다. 목록이 정해지면 여기만 갱신하면 된다.

사용법 (레포 루트에서, app 패키지 import를 위해 -m으로 실행):
    uv run python -m scripts.build_cache
"""

import asyncio

from app.core.db.databases import AsyncSessionLocal
from app.core.utils import scr_normalize
from app.repositories import cmp_repository
from app.services import (
    scr_score,
    src_europepmc_service,
    src_greenbook_service,
    src_openfda_service,
    src_opentargets_service,
)

# CLAUDE.md 기본 가중치.
WEIGHTS = {"r1": 25.0, "r2": 25.0, "r3": 25.0, "r4": 25.0, "o1": 40.0, "o2": 30.0, "o3": 30.0}

SEED_COMPOUNDS = [("carprofen", "dog")]


async def _collect_one(ingredient_name: str, species: str) -> None:
    async with AsyncSessionLocal() as db:
        compound = await cmp_repository.upsert_compound(db, ingredient_name)

        r2_raw = src_openfda_service.fetch_adverse_event_count(ingredient_name)
        r2_value = scr_normalize.r2_animal_adverse_event(r2_raw["count"]) if r2_raw else None
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "r2",
            value=r2_value,
            source_name="openFDA ADAE" if r2_raw else None,
            summary=f"이상반응 보고 {r2_raw['count']}건" if r2_raw else None,
            source_url="https://open.fda.gov/apis/animalandveterinary/event/" if r2_raw else None,
            raw_json=r2_raw["raw"] if r2_raw else None,
        )

        r1_raw = src_opentargets_service.fetch_drug_warnings(ingredient_name)
        r1_value = scr_normalize.r1_clinical_warning(r1_raw["warnings"]) if r1_raw else None
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "r1",
            value=r1_value,
            source_name="Open Targets" if r1_raw else None,
            summary=f"경고 이력 {len(r1_raw['warnings'])}건" if r1_raw else None,
            source_url="https://platform.opentargets.org/" if r1_raw else None,
            raw_json=r1_raw["raw"] if r1_raw else None,
        )

        r3_raw = src_greenbook_service.fetch_voluntary_withdrawals(ingredient_name)
        r3_value = scr_normalize.r3_voluntary_withdrawal(r3_raw["withdrawals"]) if r3_raw else None
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "r3",
            value=r3_value,
            source_name="FDA Green Book" if r3_raw else None,
            summary=f"자발적 승인철회 기록 {len(r3_raw['withdrawals'])}건" if r3_raw else None,
            source_url="https://animaldrugsatfda.fda.gov/adafda/views/#/home" if r3_raw else None,
            raw_json=r3_raw["withdrawals"] if r3_raw else None,
        )

        o1_raw = src_europepmc_service.fetch_literature_count(ingredient_name, species)
        o1_value = scr_normalize.o1_literature_scarcity(o1_raw["count"]) if o1_raw else None
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "o1",
            value=o1_value,
            source_name="Europe PMC" if o1_raw else None,
            summary=f"관련 문헌 {o1_raw['count']}건" if o1_raw else None,
            source_url="https://europepmc.org/" if o1_raw else None,
            raw_json=o1_raw["raw"] if o1_raw else None,
        )

        risk = {
            "r1": (r1_value, WEIGHTS["r1"]),
            "r2": (r2_value, WEIGHTS["r2"]),
            "r3": (r3_value, WEIGHTS["r3"]),
            "r4": (None, WEIGHTS["r4"]),
        }
        opportunity = {
            "o1": (o1_value, WEIGHTS["o1"]),
            "o2": (None, WEIGHTS["o2"]),
            "o3": (None, WEIGHTS["o3"]),
        }
        score = scr_score.calc_risk_opportunity(risk, opportunity)
        await cmp_repository.upsert_score(
            db,
            compound.id,
            species,
            risk_index=score["risk_index"],
            risk_coverage=score["risk_coverage"],
            opportunity_index=score["opportunity_index"],
            opportunity_coverage=score["opportunity_coverage"],
        )

        await db.commit()
        print(f"{ingredient_name}/{species} 저장 완료: {score}")


async def main() -> None:
    for ingredient_name, species in SEED_COMPOUNDS:
        await _collect_one(ingredient_name, species)


if __name__ == "__main__":
    asyncio.run(main())
