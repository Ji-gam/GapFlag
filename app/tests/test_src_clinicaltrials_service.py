import json
from pathlib import Path

import httpx

from app.services import src_clinicaltrials_service

FIXTURES = Path(__file__).parent / "fixtures"


def _client_returning(fixture_name: str) -> httpx.Client:
    body = json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_trial_count_found() -> None:
    client = _client_returning("clinicaltrials_search_found.json")

    result = src_clinicaltrials_service.fetch_trial_count("carprofen", client=client)

    assert result is not None
    assert result["ingredient_name"] == "carprofen"
    assert result["count"] == 2
    assert "raw" in result


def test_fetch_trial_count_zero_hits_is_valid_result() -> None:
    client = _client_returning("clinicaltrials_search_empty.json")

    result = src_clinicaltrials_service.fetch_trial_count("unknown-ingredient-xyz", client=client)

    assert result is not None
    assert result["count"] == 0


def test_fetch_trial_count_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_clinicaltrials_service.fetch_trial_count("carprofen", client=client)

    assert result is None
