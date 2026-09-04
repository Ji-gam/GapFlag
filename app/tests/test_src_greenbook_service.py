import httpx

from app.services import src_greenbook_service

HEADER = ["Application Number", "Date Withdrawn", "Ingredients", "Sponsor When Withdrawn"]

# 실제 Green Book Section 6 export에서 확인한 형태(다건 성분이 콤마로 들어감)를 그대로 씀.
ROWS = [
    ["005-414", "01/06/2014", "Roxarsone", "Zoetis Inc."],
    ["006-475", "11/03/1994", "Butacaine Sulfate, Nitrofurazone", "SmithKline Beecham Animal Health"],
]


def test_find_withdrawals_matches_single_ingredient_row() -> None:
    result = src_greenbook_service.find_withdrawals(HEADER, ROWS, "roxarsone")

    assert result is not None
    assert len(result) == 1
    assert result[0]["application_number"] == "005-414"


def test_find_withdrawals_matches_within_comma_separated_ingredients() -> None:
    result = src_greenbook_service.find_withdrawals(HEADER, ROWS, "Nitrofurazone")

    assert result is not None
    assert len(result) == 1
    assert result[0]["sponsor"] == "SmithKline Beecham Animal Health"


def test_find_withdrawals_no_match_returns_empty_list() -> None:
    result = src_greenbook_service.find_withdrawals(HEADER, ROWS, "carprofen")

    assert result == []


def test_find_withdrawals_missing_required_column_returns_none() -> None:
    result = src_greenbook_service.find_withdrawals(["Application Number"], [["005-414"]], "roxarsone")

    assert result is None


def test_fetch_voluntary_withdrawals_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_greenbook_service.fetch_voluntary_withdrawals("carprofen", client=client)

    assert result is None


def test_fetch_voluntary_withdrawals_not_an_xls_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not an xls file")

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_greenbook_service.fetch_voluntary_withdrawals("carprofen", client=client)

    assert result is None


ACTIVE_INGREDIENTS_HEADER = ["Application Number", "Active Ingredients", "Trade Name", "Ingredient"]
ACTIVE_INGREDIENTS_ROWS = [
    ["015-030", "Acepromazine Maleate", "PromAce Injectable", "Acepromazine Maleate"],
    ["200-757", "Butacaine Sulfate, Nitrofurazone", "Combo Product", "Butacaine Sulfate"],
]


def test_find_approved_ingredients_matches_single_ingredient_row() -> None:
    result = src_greenbook_service.find_approved_ingredients(ACTIVE_INGREDIENTS_HEADER, ACTIVE_INGREDIENTS_ROWS)

    assert result is not None
    assert "acepromazine maleate" in result


def test_find_approved_ingredients_matches_within_comma_separated_ingredients() -> None:
    result = src_greenbook_service.find_approved_ingredients(ACTIVE_INGREDIENTS_HEADER, ACTIVE_INGREDIENTS_ROWS)

    assert result is not None
    assert "nitrofurazone" in result


def test_find_approved_ingredients_no_match_absent_from_set() -> None:
    result = src_greenbook_service.find_approved_ingredients(ACTIVE_INGREDIENTS_HEADER, ACTIVE_INGREDIENTS_ROWS)

    assert result is not None
    assert "carprofen" not in result


def test_find_approved_ingredients_missing_required_column_returns_none() -> None:
    result = src_greenbook_service.find_approved_ingredients(["Application Number"], [["005-414"]])

    assert result is None


def test_fetch_approved_ingredients_network_failure_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_greenbook_service.fetch_approved_ingredients(client=client)

    assert result is None


def test_fetch_approved_ingredients_not_an_xls_returns_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not an xls file")

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = src_greenbook_service.fetch_approved_ingredients(client=client)

    assert result is None
