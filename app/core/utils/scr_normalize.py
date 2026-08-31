"""원자료 건수를 0~100 위험/기회 점수로 환산 (순수 함수, I/O 금지). CLAUDE.md/SESSION_HANDOFF §4-2 산식."""

import math


def r2_animal_adverse_event(count: int) -> float:
    """동물 이상반응 보고 건수 → 위험 점수. 건수가 많을수록 위험이 높다."""
    return min(100.0, 25.0 * math.log10(count + 1))


def o1_literature_scarcity(count: int) -> float:
    """관련 문헌 건수 → 문헌 희소성 점수. 문헌이 적을수록 기회(공백) 점수가 높다."""
    return max(0.0, 100.0 - 30.0 * math.log10(count + 1))
