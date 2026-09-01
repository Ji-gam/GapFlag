"""ClinicalTrials.gov 사람 임상시험 건수 수집 (O2 임상 부재 원자료). CLAUDE.md: httpx만, dict 반환."""

import httpx

BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def fetch_trial_count(ingredient_name: str, client: httpx.Client | None = None) -> dict | None:
    """성분명으로 등록된 사람 임상시험 건수를 조회한다.

    반환: {"ingredient_name", "count", "raw"} 또는 조회 실패 시 None (O2는 NULL 유지).
    매칭 0건은 HTTP 200 + totalCount=0으로 응답한다(실패가 아니라 확인함·없음).
    fields=NCTId로 제한해 study 본문(수 KB)이 raw에 딸려오지 않게 한다.
    """
    params: dict[str, str | int] = {
        "query.intr": ingredient_name,
        "countTotal": "true",
        "pageSize": 1,
        "fields": "NCTId",
        "format": "json",
    }

    owns_client = client is None
    client = client or httpx.Client(timeout=10.0)
    try:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            client.close()

    total_count = data.get("totalCount")
    if total_count is None:
        return None
    return {"ingredient_name": ingredient_name, "count": total_count, "raw": data}
