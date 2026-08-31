import json
from pathlib import Path

import httpx

from app.services import src_opentargets_service

FIXTURES = Path(__file__).parent / "fixtures"


def _load(fixture_name: str) -> dict:
    return json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))


def _client_with(search_fixture: str, drug_fixture: str | None) -> httpx.Client:
    search_body = _load(search_fixture)
    drug_body = _load(drug_fixture) if drug_fixture else None

    def handler(request: httpx.Request) -> httpx.Response:
        query = json.loads(request.content)["query"]
        body = drug_body if "query Drug" in query else search_body
        assert body is not None
        return httpx.Response(200, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_drug_warnings_found_withdrawn() -> None:
    client = _client_with("opentargets_search_found.json", "opentargets_drug_withdrawn.json")

    result = src_opentargets_service.fetch_drug_warnings("rofecoxib", client=client)

    assert result is not None
    assert result["chembl_id"] == "CHEMBL122"
    assert len(result["warnings"]) == 2
    assert result["warnings"][0]["warningType"] == "Withdrawn"


def test_fetch_drug_warnings_found_no_warnings() -> None:
    client = _client_with("opentargets_search_found.json", "opentargets_drug_no_warnings.json")

    result = src_opentargets_service.fetch_drug_warnings("carprofen", client=client)

    assert result is not None
    assert result["warnings"] == []


def test_fetch_drug_warnings_not_in_chembl_returns_none() -> None:
    client = _client_with("opentargets_search_empty.json", None)

    result = src_opentargets_service.fetch_drug_warnings("unknown-ingredient-xyz", client=client)

    assert result is None


def test_fetch_drug_warnings_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_opentargets_service.fetch_drug_warnings("rofecoxib", client=client)

    assert result is None
