"""약관 정적 카탈로그. "현재 유효한 약관이 무엇인지"의 유일한 출처.

약관 목록을 DB 테이블로 두지 않고 코드 상수로 두는 이유: 목록은 배포 단위로만 바뀌는데
테이블로 두면 관리자 화면·시딩·환경별 데이터 동기화가 전부 따라붙는다. DB에는 사용자별
'동의 결과'(TermsAgreement)만 남긴다. 약관 관리자 기능이 실제로 필요해지면 그때 옮긴다.

개정 절차: 문안을 고치면 반드시 version을 올린다. 그러면 구버전 동의를 들고 있는 사용자는
require_reagreement()로 걸러지고, 구버전으로 제출된 동의는 409로 거부되어 재동의로 유도된다.
버전을 올리지 않고 문안만 바꾸면 "무엇에 동의했는지"의 법적 근거가 사라진다.
"""

from dataclasses import dataclass
from enum import StrEnum

from . import config


class TermsType(StrEnum):
    SERVICE = "service"  # 서비스 이용약관
    PRIVACY = "privacy"  # 개인정보 수집·이용
    MARKETING = "marketing"  # 광고·뉴스레터 수신 (선택)


@dataclass(frozen=True)
class TermSpec:
    terms_type: TermsType
    version: str
    title: str
    url: str
    is_required: bool
    # 동의를 나중에 철회할 수 있는 항목인지. 필수 약관은 철회 = 서비스 이용 불가라
    # 철회 대신 회원탈퇴로 처리한다. 선택 항목만 켜고 끌 수 있다.
    revocable: bool = False


TERMS_CATALOG: tuple[TermSpec, ...] = (
    TermSpec(TermsType.SERVICE, "1.0", "서비스 이용약관", f"{config.FRONTEND_BASE_URL}/terms/service", True),
    TermSpec(TermsType.PRIVACY, "1.0", "개인정보 수집·이용 동의", f"{config.FRONTEND_BASE_URL}/terms/privacy", True),
    TermSpec(
        TermsType.MARKETING,
        "1.0",
        "광고성 정보 수신 동의",
        f"{config.FRONTEND_BASE_URL}/terms/marketing",
        False,
        revocable=True,
    ),
)

CATALOG_BY_TYPE: dict[str, TermSpec] = {str(spec.terms_type): spec for spec in TERMS_CATALOG}
REQUIRED_TYPES: frozenset[str] = frozenset(str(s.terms_type) for s in TERMS_CATALOG if s.is_required)


def current_version(terms_type: str) -> str | None:
    spec = CATALOG_BY_TYPE.get(terms_type)
    return spec.version if spec else None
