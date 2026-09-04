"""원자료 건수를 0~100 위험/기회 점수로 환산 (순수 함수, I/O 금지). CLAUDE.md/SESSION_HANDOFF §4-2 산식."""

import math


def r2_animal_adverse_event(count: int) -> float:
    """동물 이상반응 보고 건수 → 위험 점수. 건수가 많을수록 위험이 높다."""
    return min(100.0, 25.0 * math.log10(count + 1))


def o1_literature_scarcity(count: int) -> float:
    """관련 문헌 건수 → 문헌 희소성 점수. 문헌이 적을수록 기회(공백) 점수가 높다."""
    return max(0.0, 100.0 - 30.0 * math.log10(count + 1))


def o2_clinical_absence(count: int) -> float:
    """사람 임상시험(ClinicalTrials.gov) 건수 → 임상 부재 점수. 임상이 없을수록 기회가 크다."""
    if count == 0:
        return 100.0
    return max(0.0, 100.0 - 40.0 * math.log10(count + 1))


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


def o3_unapproved(approved: bool) -> float:
    """Green Book Section2 승인목록 존재 여부 → 미승인 점수. 승인 안 됐을수록 기회가 크다.

    ponytail: Section2에 종(dog/cat) 컬럼이 없어 성분 단위로만 판정한다(R3와 같은 단순화).
    종별 조인이 필요해지면 별도 소스 연동으로 대체.
    """
    return 0.0 if approved else 100.0


def r4_patent_density(count: int) -> float:
    """미국 등록특허 건수(PatentsView) → 특허 밀집도 위험 점수. 특허가 빽빽할수록 진입장벽이 높다.

    ponytail: 원 규격은 EPO OPS 패밀리 수였으나 PatentsView는 미국 등록특허만 센다.
    전세계 패밀리 기준이 필요해지면 EPO OPS 연동으로 대체.
    """
    return min(100.0, 30.0 * math.log10(count + 1))


def r3_voluntary_withdrawal(withdrawals: list[dict], approved: bool | None = None) -> float | None:
    """Green Book Section 6(자발적 승인철회) 기록 + Section 2(승인목록) → 위험 점수.

    철회 100 · 승인 유지 20 · 둘 다 확인 안 됨(approved=None) NULL.
    o3_unapproved와 같은 Section 2 승인목록을 재사용한다.
    """
    if withdrawals:
        return 100.0
    if approved is None:
        return None
    return 20.0 if approved else 0.0
