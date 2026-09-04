"""외부 API에서 성분 데이터를 수집해 DB에 저장 (수동 실행, CLAUDE.md: 화면은 DB만 읽는다).

현재 R1(Open Targets)·R2(openFDA)·R3(Green Book)·O1(Europe PMC)·O2(ClinicalTrials.gov)·
O3(Green Book Section2)까지 수집한다. R4는 EPO 키 승인 대기 중이라 아직 NULL로 남는다
(Tier2 stub, CLAUDE.md §11) — 산식이 NULL을 견디도록 설계돼 있어 서비스를 추가해도
이 스크립트의 계산 로직은 바뀌지 않는다.

대상 성분 목록은 data/seed_compounds.csv (ingredient_name,species,note)에서 읽는다.
목록을 바꾸려면 그 CSV만 고치면 된다 — 이 스크립트는 건드릴 필요 없다.

사용법 (레포 루트에서, app 패키지 import를 위해 -m으로 실행):
    uv run python -m scripts.build_cache
"""

import asyncio
import csv
import sys
import time
from pathlib import Path

import httpx

from app.core.db.databases import AsyncSessionLocal
from app.core.utils import scr_normalize
from app.repositories import cmp_repository
from app.services import (
    scr_score,
    src_clinicaltrials_service,
    src_europepmc_service,
    src_greenbook_service,
    src_openfda_service,
    src_opentargets_service,
)

# CLAUDE.md 기본 가중치.
WEIGHTS = {"r1": 25.0, "r2": 25.0, "r3": 25.0, "r4": 25.0, "o1": 40.0, "o2": 30.0, "o3": 30.0}

SEED_CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "seed_compounds.csv"


def load_seed_compounds() -> list[tuple[str, str]]:
    if not SEED_CSV_PATH.exists():
        sys.exit(f"{SEED_CSV_PATH} 가 없습니다. data/seed_compounds.csv를 먼저 만드세요.")
    with SEED_CSV_PATH.open(encoding="utf-8") as f:
        return [(row["ingredient_name"].strip().lower(), row["species"].strip().lower()) for row in csv.DictReader(f)]


async def _collect_one(
    ingredient_name: str, species: str, greenbook_client: httpx.Client, approved_ingredients: set[str] | None
) -> None:
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

        r3_raw = src_greenbook_service.fetch_voluntary_withdrawals(ingredient_name, client=greenbook_client)
        r3_approved = ingredient_name in approved_ingredients if approved_ingredients is not None else None
        r3_value = scr_normalize.r3_voluntary_withdrawal(r3_raw["withdrawals"], r3_approved) if r3_raw else None
        r3_summary = None
        if r3_raw:
            r3_summary = (
                f"자발적 승인철회 기록 {len(r3_raw['withdrawals'])}건"
                if r3_raw["withdrawals"]
                else ("승인유지 확인됨" if r3_approved else "승인철회 기록 없음, 승인여부 미확인")
            )
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "r3",
            value=r3_value,
            source_name="FDA Green Book" if r3_raw else None,
            summary=r3_summary,
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

        o3_value = (
            scr_normalize.o3_unapproved(ingredient_name in approved_ingredients)
            if approved_ingredients is not None
            else None
        )
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "o3",
            value=o3_value,
            source_name="FDA Green Book Section2" if approved_ingredients is not None else None,
            summary=(
                ("승인목록에 있음" if ingredient_name in approved_ingredients else "승인목록에 없음")
                if approved_ingredients is not None
                else None
            ),
            source_url=src_greenbook_service.ACTIVE_INGREDIENTS_URL if approved_ingredients is not None else None,
            raw_json=None,
        )

        o2_raw = src_clinicaltrials_service.fetch_trial_count(ingredient_name)
        o2_value = scr_normalize.o2_clinical_absence(o2_raw["count"]) if o2_raw else None
        await cmp_repository.upsert_evidence(
            db,
            compound.id,
            species,
            "o2",
            value=o2_value,
            source_name="ClinicalTrials.gov" if o2_raw else None,
            summary=f"사람 임상시험 {o2_raw['count']}건" if o2_raw else None,
            source_url="https://clinicaltrials.gov/" if o2_raw else None,
            raw_json=o2_raw["raw"] if o2_raw else None,
        )

        risk = {
            "r1": (r1_value, WEIGHTS["r1"]),
            "r2": (r2_value, WEIGHTS["r2"]),
            "r3": (r3_value, WEIGHTS["r3"]),
            "r4": (None, WEIGHTS["r4"]),
        }
        opportunity = {
            "o1": (o1_value, WEIGHTS["o1"]),
            "o2": (o2_value, WEIGHTS["o2"]),
            "o3": (o3_value, WEIGHTS["o3"]),
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
    compounds = load_seed_compounds()
    ok = 0
    failed: list[str] = []
    with httpx.Client(timeout=20.0) as greenbook_client:
        approved_ingredients = src_greenbook_service.fetch_approved_ingredients(client=greenbook_client)
        for i, (ingredient_name, species) in enumerate(compounds):
            if i > 0:
                time.sleep(1)  # 외부 API 4종 순차 호출 — 레이트리밋 대책
            try:
                await _collect_one(ingredient_name, species, greenbook_client, approved_ingredients)
                ok += 1
            except Exception as exc:  # noqa: BLE001 - 한 성분 실패가 배치를 죽이면 안 됨
                failed.append(f"{ingredient_name}/{species}")
                print(f"{ingredient_name}/{species} 실패: {exc}")
    print(f"완료: 성공 {ok} / 실패 {len(failed)}{' (' + ', '.join(failed) + ')' if failed else ''}")


if __name__ == "__main__":
    asyncio.run(main())
