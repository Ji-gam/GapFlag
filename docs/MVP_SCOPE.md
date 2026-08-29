# MVP_SCOPE.md — MVP 기간 범위와 규칙 유예

v0.1 · 이력: `git log docs/MVP_SCOPE.md`.

이 문서는 **2026-08-22 ~ 09-06 MVP 기간에 한해** `docs/CODING_RULES.md` / `AGENTS.md`의
일부 항목을 유예하기로 한 **팀 결정 기록**이다. 몰래 규칙을 어긴 것이 아니라 여기에 적고
합의한 것이며, 각 항목에 되돌리는 조건을 함께 적었다.

> `AGENTS.md` §7: "실코드가 `CODING_RULES.md`와 다르면 팀합의 없는 개인작업 가능성 — 그대로
> 안 따르고 재작업 필요여부 확인". 이 문서가 그 "팀합의"의 유일한 출처다. 여기에 없는
> 규칙 이탈은 전부 재작업 대상이다.

---

## 0. 전제

| 항목 | 내용 |
|---|---|
| 팀 | 4명 (개발 경험자 1명 + 처음 코딩하는 3명), 전원 AI 보조 개발 |
| 기간 | 2026-08-22 ~ 09-06 (수업 6회 + 수업 외 개발 시간) |
| 최종 산출물 | 배포된 웹 MVP + 사업계획서 |
| 최우선 제약 | **팀원이 설치해야 하는 프로그램 수를 최소화한다** |

---

## 1. 설치 목록 (전원 3개)

| 프로그램 | 대상 | 비고 |
|---|---|---|
| Git (또는 GitHub Desktop) | 전원 | 처음이면 GUI인 GitHub Desktop 권장 |
| uv | 전원 | **Python 3.13을 uv가 설치한다** — Python 별도 설치 없음 |
| 에디터 + AI 코딩 도구 | 전원 | |
| Docker Desktop | **이은호만, 배포 직전** | MySQL 최종 확인 및 배포 |

설치하지 않는 것: **Python 설치 프로그램 · Node.js · MySQL · Docker Desktop(3명)**

### 최초 셋업 (Windows PowerShell)

```powershell
# uv 설치
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 저장소 루트에서
uv python install 3.13
uv sync --group app --group dev        # ai 그룹은 넣지 않는다 (§2-1)
Copy-Item envs\example.local.env .env  # 심볼릭 링크 대신 복사 (§2-5)

# 실행
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

`http://localhost:8000/health` 에서 `{"status":"ok"}` 가 나오면 셋업 완료.
Swagger는 `http://localhost:8000/api/docs`.

---

## 2. 유예 항목

### 2-1. `ai` 의존성 그룹 미설치 · `ai_worker/` 미사용

- **결정**: 로컬·CI 모두 `uv sync --group app --group dev` 만 사용한다.
- **이유**: `ai` 그룹에 torch + sentence-transformers가 있어 최초 1회 약 2GB를 받고
  프로세스가 1.1GB를 점유한다(`envs/example.local.env` 주석). 처음 개발하는 팀원이
  첫날 여기서 막힌다. MVP는 근거 제시형 도구이므로 LLM/RAG가 필요하지 않다.
- **부수 변경**: `.github/workflows/ci.yml`의 `uv sync --all-groups` → `--group app --group dev`.
  `pyproject.toml`에 langchain/torch/chroma 등의 `ignore_missing_imports` 예외를 추가해
  `mypy .` 가 그대로 통과하게 했다.
- **되돌리는 조건**: `ai_worker/`에 실제 코드를 작성하기로 결정한 시점.
  CI를 `--all-groups` / `mypy .`로 되돌리고 `pyproject.toml`의 해당 override 블록을 삭제한다.

### 2-2. 로컬 DB는 SQLite, 배포는 MySQL

- **결정**: `app/core/config.py`의 `DATABASE_URL` 기본값을
  `sqlite+aiosqlite:///./data/gapflag.db` 로 둔다. 배포 시 `.env`에서 MySQL URL로 교체한다.
- **이유**:
  - MySQL 설치를 전원에게 요구하지 않기 위해서다. `aiosqlite`는 이미 `dev` 그룹에 있어
    새로 설치할 것이 없다.
  - **비동기 드라이버 그대로이므로 Repository 계층 코드는 한 줄도 달라지지 않는다.**
    `CODING_RULES.md` §1의 `AsyncSession` 규칙을 그대로 지킨다.
  - `docs/TROUBLESHOOTING.md` A(로컬 MySQL 데이터 충돌) / B(3306 포트 충돌)가
    구조적으로 발생하지 않는다.
- **한계**: SQLite와 MySQL은 타입 강제·ALTER 지원·문자열 정렬이 다르다. 스키마가
  4개 테이블 규모라 실질 차이는 없지만, **배포 전에 반드시 MySQL로 한 번 마이그레이션과
  주요 조회를 검증한다**(§4 체크리스트).
- **부수 변경**: `app/core/db/databases.py`, `app/core/db/migrations/env.py`가 두 곳에
  하드코딩하고 있던 URL을 `config.DATABASE_URL` 한 곳으로 통합. SQLite용으로
  Alembic `render_as_batch=True` 를 켰다(ALTER 제약 회피).
- **되돌리는 조건**: 배포 시. `.env`의 `DATABASE_URL`만 바꾸면 되고 코드 변경은 없다.

### 2-3. 화면은 Jinja2 서버 사이드 템플릿 · React 유예

- **결정**: MVP 화면은 `app/templates/` 의 Jinja2 템플릿으로 만든다.
  `frontend/` 는 **손대지 않고 그대로 둔다**(삭제 금지).
- **이유**:
  - Node.js 설치를 요구하지 않기 위해서다. `app/core/config.py`에 `TEMPLATE_DIR`가
    이미 정의되어 있고, `fastapi[standard]`에 Jinja2가 포함되어 추가 의존성이 없다.
  - 실행 프로세스가 1개로 끝난다(uvicorn만). vite dev 서버·프록시 설정이 사라진다.
  - `CODING_RULES.md` §3-4의 `frontend/src/api/types.ts` 수동 동기화 부담이 없어진다.
- **확장 경로**: 나중에 React로 갈 때 **Service 계층을 그대로 재사용**해
  `/api/v1/...` JSON 엔드포인트만 얇게 추가한다. §1 계층 분리 덕에 버려지는 코드가 없다.
- **HTML 라우터 위치**: `/api/v1` 아래는 JSON 전용(§11-1)이므로 HTML 페이지 라우터는
  `app/apis/cmp_pages.py` 에 두고 `app/main.py` 에 직접 등록한다.
  이는 템플릿에 없는 배치이며 이 문서가 근거다.
- **스타일**: `CODING_RULES.md` §3-5 최소선 유지. Tailwind·shadcn 도입 유예.
- **차트**: 차트 라이브러리를 추가하지 않는다. 2×2 매트릭스는 Jinja2에서
  **인라인 SVG**로 그린다(`<circle>` + `<title>` 툴팁).

### 2-4. 로그인·인증 미적용

- **결정**: `auth_kit` 은 `app/main.py` / `app/apis/v1/__init__.py` 의 주석 상태를 유지한다.
- **이유**: MVP는 단일 사용자용 조회 도구다. 인증은 요구사항 범위 밖.
- **되돌리는 조건**: 사용자별 조회 이력 저장이 필요해지는 v2.0.
  `auth_kit/README.md` 대로 주석만 해제하면 된다.

### 2-5. `.env` 는 심볼릭 링크 대신 복사

- **결정**: `CODING_RULES.md` §2-2의 `ln -s envs/.local.env .env` 대신
  `Copy-Item envs\example.local.env .env` 를 쓴다.
- **이유**: Windows에서 심볼릭 링크는 관리자 권한 또는 개발자 모드가 필요하다.
- **주의**: 복사본이므로 `envs/` 원본을 고쳐도 `.env`에 반영되지 않는다.
  환경변수를 추가할 때는 **`.env`와 `envs/example.local.env` 양쪽을 고친다**.

### 2-6. ERD 문서 미작성

- **결정**: `CODING_RULES.md` §6의 별도 ERD 파일을 만들지 않는다.
  `app/models/cmp_models.py` 를 스키마의 단일 창구로 삼는다.
- **이유**: 테이블이 4개뿐이고 관계가 단순하다. 두 곳을 동기화하는 비용이 이득보다 크다.
- **되돌리는 조건**: 테이블이 8개를 넘거나 도메인이 2개 이상으로 늘어날 때.

### 2-7. Celery · Redis · APScheduler 미사용

- **결정**: 외부 데이터 수집은 `scripts/build_cache.py` 를 **수동 실행**한다.
- **이유**: 워커 도입은 디버깅 비용이 크고, MVP는 발표 전날 한 번 갱신하면 충분하다.
- **되돌리는 조건**: 정기 자동 갱신이 필요해질 때. APScheduler → Celery 순서로 도입.

---

## 3. 유예하지 **않는** 것 (그대로 지킨다)

아래는 초보에게 부담이 되더라도 지킨다. 이것들이 확장성의 실체이기 때문이다.

- **계층 화살표** (`CODING_RULES.md` §1) — `apis/`는 `services/`만, `services/`는
  `repositories/`만 안다. 건너뛰기·역방향 호출 금지.
- **TDD** (§4) — 기능 1개당 정상 + 실패 테스트 2개를 같은 PR에.
  순수 함수(`app/core/utils/scr_*.py`)는 Fake도 필요 없어 가장 쉽다.
- **mypy 통과** — 기본 설정(strict 아님)이라 **함수 시그니처에 타입힌트만 붙이면**
  대체로 통과한다. `AGENTS.md` §8이 이미 요구하는 사항이다.
- **Alembic** (§12) — DB 수동 ALTER 금지.
  단, **리비전 생성은 이은호만** 한다(§5 소유권). 병렬 생성 시 head가 갈라진다.
- **API 응답 포맷** (§11-2) — `{"success":true,"data":{...},"message":null}` 고정.
  JSON 엔드포인트를 나중에 추가할 때도 이 계약을 지킨다.
- **Swagger 문서화** (§5) — `summary` / `description` / `responses` / `Field(description=...)`.
- **GitFlow + PR** (`CONTRIBUTING.md` §3, §4) — `feature/*` → `dev` PR, 200~300줄 슬라이스.
- **`.env`·API 키 커밋 금지** (§9).

---

## 4. MVP 범위

### 4-1. 도메인 코드 (한 번 정하면 새로 만들지 않는다 — `CODING_RULES.md` §2)

| 코드 | 의미 | 파일 접두어 |
|---|---|---|
| **CMP** | Compound — 성분·지수·근거 (핵심 도메인) | `cmp_*` |
| **SRC** | Source — 외부 데이터 수집 | `src_*` |
| **SCR** | Scoring — 지수 산식 | `scr_*` |

에러 코드는 `CMP_001` 형식(§11-2).

### 4-2. 파일 배치

```
app/
├─ models/cmp_models.py              Compound / CompoundScore / CompoundEvidence / SpeciesAlert
├─ repositories/cmp_repository.py    AsyncSession 쿼리만
├─ services/
│  ├─ cmp_service.py                 조회 조합
│  ├─ src_openfda_service.py         외부 API 호출 (Service 담당 — §1에서 허용)
│  ├─ src_greenbook_service.py
│  ├─ src_europepmc_service.py
│  ├─ src_opentargets_service.py
│  └─ src_epo_service.py
├─ core/utils/
│  ├─ scr_normalize.py               순수 함수 (I/O 없음)
│  └─ scr_index.py                   지수 계산
├─ dtos/cmp_dtos.py
├─ apis/cmp_pages.py                 HTML 페이지 (Jinja2) — §2-3
├─ templates/                        Jinja2 템플릿
└─ tests/
   ├─ cmp_apis/                      Router 통합테스트
   └─ test_scr_index.py              순수 함수 단위테스트
scripts/build_cache.py               수집 배치 진입점 (수동 실행)
data/                                SQLite (gitignore)
```

### 4-3. 화면 3개

| ID | 화면 | 우선순위 |
|---|---|---|
| S1 | 2×2 매트릭스 (기회 × 위험) | P0 |
| S2 | 성분 상세 + 근거 카드 | P0 |
| S3 | 후보 비교 | P1 (잘라도 됨) |
| S0 | 소개 · 데이터 출처 · 산식 공개 | P1 |

### 4-4. 파일 소유권 (`CONTRIBUTING.md` §2)

| 경로 | 담당 |
|---|---|
| `models/` · `repositories/` · `core/db/` · Alembic · 배포 · `pyproject.toml` · `uv.lock` | 이은호 |
| `services/src_*` · `tests/fixtures/` | 박정하 |
| `core/utils/scr_*` · `tests/test_scr_*` | 양민경 |
| `apis/cmp_pages.py` · `templates/` | 정보교 |

남의 파일은 직접 고치지 않고 GitHub 이슈로 요청한다.

### 4-5. 데이터 원칙 (타협 불가)

- **데이터 없음은 `None`. 절대 0으로 치환하지 않는다.** 점수 컬럼은 전부 nullable.
  0점("확인했고 위험 없음")과 NULL("확인하지 못함")은 다른 의미다.
- 지수 계산 시 NULL 구성요소는 분자·분모 모두에서 제외하고 **커버리지 %를 함께 표시**한다.
- 원본 API 응답(raw JSON)을 DB에 함께 저장한다 — 나중에 재계산이 가능해야 한다.
- 화면은 DB만 읽는다. 화면에서 외부 API를 직접 호출하지 않는다.
- 모든 화면 하단에 고지: **"본 도구는 참고용이며 의료·규제 판단을 대신하지 않습니다."**

### 4-6. 미완성 구성요소 처리 — `CODING_RULES.md` §8 Tier2 stub

EPO 키 발급이 늦거나 Green Book 파싱이 안 끝나면, **DTO와 Router는 최종 형태로 두고
Service 내부만 `None` 반환 stub으로 둔다.** 프론트·API 계약은 무변경.
§4-5의 NULL 설계가 그대로 이 안전장치 역할을 한다.

잘라내는 순서: ① S3 비교 화면 → ② 실시간 조회 → ③ 특허(EPO) 구성요소 →
④ Green Book(R3·O3). **절대 버리지 않는 것**: 2×2 매트릭스 / 근거 카드와 원문 링크 /
"데이터 없음" 회색 표시.

---

## 5. 배포 전 체크리스트

- [ ] `.env`의 `DATABASE_URL`을 MySQL로 바꿔 `alembic upgrade head` 성공
- [ ] MySQL에서 3개 화면 전부 정상 조회 (SQLite↔MySQL 차이 확인 — §2-2 한계)
- [ ] `uv run pytest -v` 통과 로그 확보
- [ ] `uv run ruff check .` · `uv run mypy .` 통과
- [ ] 외부 API를 전부 차단한 상태에서 전체 시연 완주 (캐시만으로)
- [ ] `.env` / API 키가 diff에 남지 않았는지 확인
- [ ] 면책 고지가 모든 화면에 있는지 확인
