"""원자료 건수를 0~100 위험/기회 점수로 환산 (순수 함수, I/O 금지). CLAUDE.md/SESSION_HANDOFF §4-2 산식."""

import math


def r2_animal_adverse_event(count: int) -> float:
    """동물 이상반응 보고 건수 → 위험 점수. 건수가 많을수록 위험이 높다."""
    return min(100.0, 25.0 * math.log10(count + 1))


def o1_literature_scarcity(count: int) -> float:
    """관련 문헌 건수 → 문헌 희소성 점수. 문헌이 적을수록 기회(공백) 점수가 높다."""
    return max(0.0, 100.0 - 30.0 * math.log10(count + 1))


def r1_clinical_warning(warnings: list[dict]) -> float:
    """Open Targets drugWarnings → 위험 점수. 철회(Withdrawn) > 블랙박스 경고 > 없음.

    ponytail: SESSION_HANDOFF.md의 "독성 100·효능부족 60·사업적 20" 3단계 분류는 ChEMBL
    drugWarnings에 사유 카테고리가 없어 재현 불가 — warningType 2종만으로 단순화함.
    사유별 세분화가 필요해지면 Open Targets evidence(studyStopReason) 연동으로 대체.
    """
    types = {w.get("warningType") for w in warnings}
    if "Withdrawn" in types:
        return 100.0
    if "Black Box Warning" in types:
        return 60.0
    return 0.0


def r3_voluntary_withdrawal(withdrawals: list[dict]) -> float:
    """Green Book Section 6(자발적 승인철회) 기록 → 위험 점수.

    ponytail: SESSION_HANDOFF.md의 "철회 100·승인 유지 20·기록 없음 NULL" 3단계는
    "승인 유지"를 확인하려면 Green Book의 별도 섹션(활성 성분 목록)과 조인이 필요해
    지금은 재현 불가 — 철회 기록 매칭 여부만으로 100/0 이진 판정한다. 승인 유지 확인이
    필요해지면 Section 2(Active Ingredients) 연동으로 20점 구간을 추가.
    """
    return 100.0 if withdrawals else 0.0
