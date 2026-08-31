"""Europe PMC 문헌 검색 수집 (O1 문헌 희소성 원자료). CLAUDE.md: httpx만, dict 반환."""

import httpx

BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

_SPECIES_TERMS = {"dog": "(dog OR canine)", "cat": "(cat OR feline)"}


def fetch_literature_count(ingredient_name: str, species: str, client: httpx.Client | None = None) -> dict | None:
    """성분명·종으로 관련 문헌 건수를 조회한다.

    반환: {"ingredient_name", "species", "count", "raw"} 또는 조회 실패 시 None (O1은 NULL 유지).
    """
    species_query = _SPECIES_TERMS.get(species.strip().lower())
    if species_query is None:
        raise ValueError(f"지원하지 않는 species: {species}")

    params: dict[str, str | int] = {
        "query": f'"{ingredient_name}" AND {species_query}',
        "format": "json",
        "pageSize": 1,
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

    hit_count = data.get("hitCount")
    if hit_count is None:
        return None
    return {"ingredient_name": ingredient_name, "species": species, "count": hit_count, "raw": data}
