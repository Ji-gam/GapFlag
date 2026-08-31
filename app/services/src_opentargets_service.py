"""Open Targets 사람 임상/시판 경고 이력 수집 (R1 원자료). CLAUDE.md: httpx만, dict 반환."""

import httpx

BASE_URL = "https://api.platform.opentargets.org/api/v4/graphql"

_SEARCH_QUERY = """
query Search($q: String!) {
  search(queryString: $q, entityNames: ["drug"]) {
    hits { id name entity }
  }
}
"""

_DRUG_WARNINGS_QUERY = """
query Drug($id: String!) {
  drug(chemblId: $id) {
    id
    name
    drugWarnings { warningType toxicityClass description year }
  }
}
"""


def fetch_drug_warnings(ingredient_name: str, client: httpx.Client | None = None) -> dict | None:
    """성분명으로 Open Targets의 사람 임상/시판 경고(철회·블랙박스 등) 이력을 조회한다.

    반환: {"ingredient_name", "chembl_id", "warnings", "raw"} 또는 조회 실패 시 None (R1은 NULL 유지).
    ChEMBL 검색 결과가 0건이면(성분 자체가 없음) 확인 불가로 보고 None을 반환한다.
    """
    owns_client = client is None
    client = client or httpx.Client(timeout=10.0)
    try:
        search_resp = client.post(BASE_URL, json={"query": _SEARCH_QUERY, "variables": {"q": ingredient_name}})
        search_resp.raise_for_status()
        hits = search_resp.json().get("data", {}).get("search", {}).get("hits", [])
        chembl_id = next((h["id"] for h in hits if h.get("entity") == "drug"), None)
        if chembl_id is None:
            return None

        drug_resp = client.post(BASE_URL, json={"query": _DRUG_WARNINGS_QUERY, "variables": {"id": chembl_id}})
        drug_resp.raise_for_status()
        data = drug_resp.json()
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            client.close()

    drug = data.get("data", {}).get("drug")
    if drug is None:
        return None
    return {
        "ingredient_name": ingredient_name,
        "chembl_id": chembl_id,
        "warnings": drug.get("drugWarnings", []),
        "raw": data,
    }
