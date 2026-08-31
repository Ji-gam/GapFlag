"""FDA Green Book Section 6(자발적 승인철회) 수집 (R3 원자료). CLAUDE.md: httpx만, dict 반환.

공식 API가 없어 공개 Excel export를 받아 xlrd로 파싱한다(legacy .xls/BIFF8라 xlsx 전용인
openpyxl로는 못 읽음 — 승인 경위는 이슈 #16).
"""

import httpx
import xlrd

BASE_URL = (
    "https://animaldrugsatfda.fda.gov/adafda/app/search/public/voluntaryWithdrawalExcel/Section6VoluntaryWithdrawal"
)

_REQUIRED_COLUMNS = {"Application Number", "Date Withdrawn", "Ingredients", "Sponsor When Withdrawn"}


def find_withdrawals(header: list[str], rows: list[list], ingredient_name: str) -> list[dict] | None:
    """헤더/행 목록에서 성분명과 일치하는 자발적 철회 기록을 찾는다.

    한 행의 Ingredients 컬럼은 "A, B" 처럼 여러 성분이 콤마로 들어있어 정확히 나눠 비교한다.
    필수 컬럼이 없으면(export 포맷이 바뀐 경우) None을 반환해 잘못된 빈 결과와 구분한다.
    """
    col = {name: i for i, name in enumerate(header)}
    if not _REQUIRED_COLUMNS <= col.keys():
        return None

    target = ingredient_name.strip().lower()
    matches = []
    for row in rows:
        ingredients = [i.strip().lower() for i in str(row[col["Ingredients"]]).split(",")]
        if target in ingredients:
            matches.append(
                {
                    "application_number": row[col["Application Number"]],
                    "date_withdrawn": row[col["Date Withdrawn"]],
                    "ingredients": row[col["Ingredients"]],
                    "sponsor": row[col["Sponsor When Withdrawn"]],
                }
            )
    return matches


def fetch_voluntary_withdrawals(ingredient_name: str, client: httpx.Client | None = None) -> dict | None:
    """성분명으로 Green Book의 자발적 승인철회 이력을 조회한다.

    반환: {"ingredient_name", "withdrawals"} 또는 조회/파싱 실패 시 None (R3는 NULL 유지).
    withdrawals가 빈 리스트면 "확인했으나 철회 기록 없음"(0점), None이면 확인 불가.
    원본 스프레드시트 전체(수백 행)를 매 성분마다 raw로 통째로 저장하는 건 낭비라
    매칭된 행만 담아 evidence의 raw_json으로 쓴다.
    """
    owns_client = client is None
    client = client or httpx.Client(timeout=20.0)
    try:
        response = client.get(BASE_URL)
        response.raise_for_status()
        content = response.content
    except httpx.HTTPError:
        return None
    finally:
        if owns_client:
            client.close()

    try:
        book = xlrd.open_workbook(file_contents=content)
        sheet = book.sheet_by_index(0)
        header = sheet.row_values(0)
        rows = [sheet.row_values(r) for r in range(1, sheet.nrows)]
    except xlrd.XLRDError:
        return None

    withdrawals = find_withdrawals(header, rows, ingredient_name)
    if withdrawals is None:
        return None
    return {"ingredient_name": ingredient_name, "withdrawals": withdrawals}
