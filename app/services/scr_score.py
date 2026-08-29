"""위험·기회 지수 계산 (순수 함수, I/O 금지). CLAUDE.md 지수 산식 §참고."""


def calc_index(components: dict[str, tuple[float | None, float]]) -> tuple[float | None, float]:
    """components: {키: (값 또는 None, 가중치)}. NULL은 분자·분모에서 제외.

    반환: (지수 0~100 또는 전부 NULL이면 None, 커버리지 0~1)
    """
    known = [(v, w) for v, w in components.values() if v is not None]
    coverage = len(known) / len(components) if components else 0.0
    if not known:
        return None, coverage
    weighted_sum = sum(v * w for v, w in known)
    weight_total = sum(w for _, w in known)
    return weighted_sum / weight_total, coverage


def calc_risk_opportunity(
    risk: dict[str, tuple[float | None, float]], opportunity: dict[str, tuple[float | None, float]]
):
    risk_index, risk_coverage = calc_index(risk)
    opp_index, opp_coverage = calc_index(opportunity)
    return {
        "risk_index": risk_index,
        "risk_coverage": risk_coverage,
        "opportunity_index": opp_index,
        "opportunity_coverage": opp_coverage,
    }


def _demo() -> None:
    risk = {
        "r1": (None, 25.0),
        "r2": (45.0, 25.0),
        "r3": (20.0, 25.0),
        "r4": (None, 25.0),
    }
    opportunity = {
        "o1": (60.0, 40.0),
        "o2": (None, 30.0),
        "o3": (0.0, 30.0),
    }
    result = calc_risk_opportunity(risk, opportunity)
    assert result["risk_index"] == (45.0 * 25 + 20.0 * 25) / 50, result
    assert result["risk_coverage"] == 0.5, result
    assert result["opportunity_index"] == (60.0 * 40 + 0.0 * 30) / 70, result
    assert abs(result["opportunity_coverage"] - 2 / 3) < 1e-9, result
    assert calc_index({})[0] is None
    print("scr_score._demo ok")


if __name__ == "__main__":
    _demo()
