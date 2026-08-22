# Gap & Flag 개발 규칙

## 프로젝트

동물용 의약품의 타깃·성분을 고를 때, 연구 공백(기회)과 위험 신호를 한 화면에서
교차 검증해 "왜 아무도 이걸 하지 않았는지"까지 답해주는 스크리닝 도구.

2026 KU AI Nest AI 창업 실전 프로그램 (2026.8.22 ~ 9.6) 과제.
팀원 4명 중 3명이 개발 초보이며, 전원 AI 보조로 개발한다.

기본 규칙은 `AGENTS.md`/`docs/CODING_RULES.md`(기존 FastAPI 스켈레톤 템플릿)를 따른다.
MVP 기간 유예 항목은 `docs/MVP_SCOPE.md`, 개발 초보 3명용 실습 순서는 `docs/BEGINNER_GUIDE.md` 참고.

## 스택 — 반드시 이 버전 문법으로

- Python 3.13, **FastAPI**(템플릿 그대로) + **Jinja2** 서버 사이드 템플릿(`app/templates/`)
  - Streamlit 아님. React(`frontend/`)도 MVP 기간엔 쓰지 않음 — `docs/MVP_SCOPE.md`
- **SQLAlchemy 2.0 스타일 + `AsyncSession`**(템플릿 그대로): `DeclarativeBase`, `Mapped` / `mapped_column`, `select()`
  - 금지: `declarative_base()`, `Column()`, `session.query()`
- **Pydantic v2**: `field_validator`, `model_config = ConfigDict(...)`
  - 금지: `@validator`, `class Config`
- DB는 로컬 **SQLite**(`config.DATABASE_URL` 기본값), 배포는 **MySQL** — 접속 문자열만 다름
- `uv sync --group app --group dev`만 사용. `--group ai`(torch/langchain) 설치 금지

## 아키텍처 규칙 — 위반 시 리뷰 반려

템플릿의 Router → Service → Repository 계층을 그대로 따른다.

- HTML 페이지 라우터는 `/api/v1` 아래(JSON 전용)가 아니라 `app/apis/cmp_pages.py`에 두고 `main.py`에 직접 등록
- 수집(`app/services/cmp_*.py`) : 외부 API 호출은 `requests`/`httpx`만. dict 반환
- 점수 계산(`app/services/scr_*.py`) : 표준 라이브러리 외 import 금지. 순수 함수. I/O 금지
- 원본 API 응답(raw JSON)을 DB에 함께 저장한다
- 화면은 DB만 읽는다. 화면에서 외부 API를 직접 호출하지 않는다

## 데이터 원칙 — 타협 불가

- **데이터 없음은 `None`이다. 절대 0으로 치환하지 않는다**
- 점수 컬럼은 nullable. NULL과 0점은 다른 의미다
  (0점 = 확인했고 위험 없음 / NULL = 확인하지 못함)
- 지수 계산 시 NULL 구성요소는 제외하고, 커버리지 %를 함께 표시한다
- 화면에서 "데이터 없음"은 회색으로 표시하고
  "위험이 없다는 뜻이 아닙니다" 문구를 함께 노출한다

## 금지

- **새 의존성 추가 금지.** `uv.lock`에 있는 것만 사용한다. `uv.lock`은 이은호 씨만 수정
- **pandas, plotly 사용 금지**. 차트는 Jinja2 템플릿 안 인라인 SVG
- MVP 기간 `ai` 그룹(LangChain, torch, Chroma 등) 미사용 — `docs/MVP_SCOPE.md`
- 인증(`auth_kit`) 미사용 — `app/main.py`에서 계속 주석 처리

## 테스트

- 새 함수는 **테스트를 먼저 작성**한다. 기대값은 사람이 정한다
- 외부 API 연동 코드는 `app/tests/fixtures/`의 저장된 응답으로 테스트한다 (실 API 호출 금지)
- 점수 계산은 손으로 계산한 기대값으로 검증한다

## 지수 산식 (요약)

```
위험 지수 = Σ(wᵢ × Rᵢ) / Σ(wᵢ)     R1 임상중단 · R2 동물이상반응
                                      R3 승인철회 · R4 특허밀집도
기회 지수 = Σ(wⱼ × Oⱼ) / Σ(wⱼ)     O1 문헌희소성 · O2 임상부재 · O3 미승인

NULL인 구성요소는 분자·분모 모두에서 제외한다
커버리지 = 값이 있는 구성요소 수 / 전체 구성요소 수
```

기본 가중치 — 위험: 각 25 / 기회: O1 40, O2 30, O3 30
사용자가 화면에서 조정 가능해야 하며, 산식은 제품 안에서 공개한다.

## 파일 소유권

역할 분담(누가 어떤 경로를 맡을지)은 아직 확정 전 — 확정되면 `docs/MVP_SCOPE.md` 표에 채운다.
담당이 아닌 파일은 직접 수정하지 않고 GitHub 이슈로 요청한다.
DB 파일은 `.gitignore` 대상 — Alembic/스크립트로 재생성한다.

## 뒤처질 때 잘라내는 순서

1. 비교 화면 — 없어도 데모 가능
2. 실시간 조회 — 캐시만으로 시연
3. 특허(EPO OPS) 구성요소 — 키 발급 지연 시. 가중치 재분배로 흡수
4. Green Book 파싱 (R3·O3) — 4개 구성요소로 출시. 산식이 NULL을 견디도록 설계됨

**절대 버리지 않는 것 셋** — 2×2 매트릭스, 근거 카드와 원문 링크, "데이터 없음" 회색 표시.

## 면책 고지

모든 화면 하단에 다음 문구를 표시한다.

> 본 도구는 참고용이며 의료·규제 판단을 대신하지 않습니다.
