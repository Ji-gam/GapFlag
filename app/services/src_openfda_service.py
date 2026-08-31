"""openFDA Animal & Veterinary 이상반응(ADAE) 수집 (R2 원자료). CLAUDE.md: httpx만, dict 반환."""

import httpx

BASE_URL = "https://api.fda.gov/animalandveterinary/event.json"


def fetch_adverse_event_count(ingredient_name: str, client: httpx.Client | None = None) -> dict | None:
    """성분명으로 동물 이상반응 보고 건수를 조회한다.

    반환: {"ingredient_name", "count", "raw"} 또는 조회 실패 시 None (R2는 NULL 유지).
    매칭 0건은 openFDA가 404로 응답하며, 이는 실패가 아니라 count=0(확인함, 없음)이다.
    """
    params: dict[str, str | int] = {
        "search": f'drug.active_ingredients.name:"{ingredient_name}"',
        "limit": 1,
    }

    owns_client = client is None
    client = client or httpx.Client(timeout=10.0)
    try:
        response = client.get(BASE_URL, params=params)
        if response.status_code == 404:
            return {"ingredient_name": ingredient_name, "count": 0, "raw": response.json()}
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            client.close()

    total = data.get("meta", {}).get("results", {}).get("total")
    if total is None:
        return None
    return {"ingredient_name": ingredient_name, "count": total, "raw": data}
