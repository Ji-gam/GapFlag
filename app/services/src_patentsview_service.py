"""PatentsView Search API에서 미국 등록특허 건수를 수집 (R4 원자료). CLAUDE.md: httpx만, dict 반환."""

import json

import httpx

from app.core import config

BASE_URL = "https://search.patentsview.org/api/v1/patent/"


def fetch_patent_count(ingredient_name: str, client: httpx.Client | None = None) -> dict | None:
    """성분명으로 미국 등록특허 건수(제목·초록 검색)를 조회한다.

    반환: {"ingredient_name", "count", "raw"} 또는 조회 실패 시 None (R4는 NULL 유지).
    API 키가 비어 있으면 호출 자체를 하지 않고 None을 반환한다 — "특허 0건"이 아니라
    "아직 확인하지 못함"이다. 매칭 0건은 정상 응답의 total_hits=0이며 count=0으로 저장한다.
    """
    api_key = config.PATENTSVIEW_API_KEY
    if not api_key:
        return None

    query = {
        "_or": [
            {"_text_phrase": {"patent_title": ingredient_name}},
            {"_text_phrase": {"patent_abstract": ingredient_name}},
        ]
    }
    params = {"q": json.dumps(query), "f": json.dumps(["patent_id"]), "o": json.dumps({"size": 1})}
    headers = {"X-Api-Key": api_key}

    owns_client = client is None
    client = client or httpx.Client(timeout=10.0)
    try:
        response = client.get(BASE_URL, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            client.close()

    total = data.get("total_hits")
    if total is None:
        return None
    return {"ingredient_name": ingredient_name, "count": total, "raw": data}
