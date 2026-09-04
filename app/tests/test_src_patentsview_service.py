import json
from pathlib import Path

import httpx
import pytest

from app.core import config
from app.services import src_patentsview_service

FIXTURES = Path(__file__).parent / "fixtures"


def _client_returning(status_code: int, fixture_name: str) -> httpx.Client:
    body = json.loads((FIXTURES / fixture_name).read_text(encoding="utf-8"))

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.fixture(autouse=True)
def _api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "PATENTSVIEW_API_KEY", "test-key")


def test_fetch_patent_count_found() -> None:
    client = _client_returning(200, "patentsview_search_found.json")

    result = src_patentsview_service.fetch_patent_count("meloxicam", client=client)

    assert result is not None
    assert result["ingredient_name"] == "meloxicam"
    assert result["count"] == 132
    assert "raw" in result


def test_fetch_patent_count_empty_returns_zero_not_none() -> None:
    client = _client_returning(200, "patentsview_search_empty.json")

    result = src_patentsview_service.fetch_patent_count("unknown-ingredient-xyz", client=client)

    assert result is not None
    assert result["count"] == 0


def test_fetch_patent_count_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_patentsview_service.fetch_patent_count("meloxicam", client=client)

    assert result is None


def test_fetch_patent_count_no_api_key_returns_none_without_calling(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "PATENTSVIEW_API_KEY", "")

    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("API 키가 없으면 호출 자체를 하면 안 된다")

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_patentsview_service.fetch_patent_count("meloxicam", client=client)

    assert result is None
