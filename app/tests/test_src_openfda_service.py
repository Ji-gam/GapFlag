import json
from pathlib import Path

import httpx

from app.services import src_openfda_service

FIXTURES = Path(__file__).parent / "fixtures"


def _client_returning(status_code: int, fixture_name: str) -> httpx.Client:
    body = json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_adverse_event_count_found() -> None:
    client = _client_returning(200, "openfda_event_found.json")

    result = src_openfda_service.fetch_adverse_event_count("carprofen", client=client)

    assert result is not None
    assert result["ingredient_name"] == "carprofen"
    assert result["count"] == 452
    assert "raw" in result


def test_fetch_adverse_event_count_not_found_returns_zero_not_none() -> None:
    client = _client_returning(404, "openfda_event_not_found.json")

    result = src_openfda_service.fetch_adverse_event_count("unknown-ingredient-xyz", client=client)

    assert result is not None
    assert result["count"] == 0


def test_fetch_adverse_event_count_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_openfda_service.fetch_adverse_event_count("carprofen", client=client)

    assert result is None
