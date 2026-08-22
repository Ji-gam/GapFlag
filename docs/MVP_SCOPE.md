# MVP_SCOPE — Gap & Flag (2026.8.22 ~ 9.6)

기존 FastAPI 스켈레톤 템플릿(`AGENTS.md`, `docs/CODING_RULES.md`)을 그대로 쓰되,
아래 항목만 MVP 기간 동안 유예한다. 되돌리는 조건을 함께 적어둔다.

## 유예 항목

| 항목 | MVP | 되돌리는 조건 |
|---|---|---|
| 화면 | FastAPI + Jinja2 (`app/templates/`) | 트래픽 증가·풍부한 상호작용 필요 시 React(`frontend/`)로 전환 |
| DB | SQLite (`config.DATABASE_URL` 기본값) | 배포 시 `.env`에서 `DATABASE_URL=mysql+asyncmy://...`로 덮어씀 |
| `ai` 의존성 그룹(langchain/torch/chroma) | 미설치 | `ai_worker/`에 실제 RAG 코드가 필요해지면 `uv sync --group ai` |
| `--all-groups` CI | `--group app --group dev`만 | ai_worker 코드가 생기면 CI에 `--group ai` 잡 추가 |
| 인증(`auth_kit`) | `app/main.py`에서 주석 처리, 미사용 | 요구사항에 로그인이 추가되면 주석 해제 |
| Alembic 마이그레이션 | 스키마 확정 전까지 `alembic upgrade head` 실행 안 함 | 2회차 `cmp_models.py` 확정 후 첫 리비전 생성 |

## 설치 목록

전원: Git(또는 GitHub Desktop), `uv`, 에디터+AI 도구. Docker Desktop은 이은호만 배포 직전에.
Python/Node.js/MySQL/Docker(3명)는 설치하지 않는다.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.13
uv sync --group app --group dev
Copy-Item envs\example.local.env .env
uv run uvicorn app.main:app --reload
```

`--group ai`는 넣지 않는다 — torch + sentence-transformers가 최초 1회 약 2GB를 받고
서빙 프로세스가 1.1GB를 물고 있는다.

`.env`는 심볼릭 링크가 아니라 복사본이다(Windows 심볼릭 링크는 관리자 권한 필요).
`envs/example.local.env`를 고칠 때는 각자 `.env`도 같이 고쳐야 한다.

## 도메인 코드

CMP(성분) / SRC(수집 소스) / SCR(점수). 새 파일은 `cmp_*.py`, `src_*.py`, `scr_*.py` 접두어를 쓴다.

## 파일 배치

HTML 페이지 라우터는 `/api/v1` 아래(JSON 전용, `docs/CODING_RULES.md` §11-1)가 아니라
`app/apis/cmp_pages.py`에 두고 `main.py`에 직접 등록한다.

## 데이터 원칙

- 데이터 없음은 `None`. 0으로 치환하지 않는다
- 점수 컬럼은 nullable. NULL(확인 못함)과 0점(확인했고 위험 없음)은 다른 의미다
- 지수 계산 시 NULL 구성요소는 제외하고 커버리지 %를 함께 표시한다

## 파일 소유권

역할 분담은 아직 확정 전이다. 확정되면 이 표에 담당자를 채운다.

| 경로 | 담당 |
|---|---|
| `app/apis/cmp_*.py`, `app/services/cmp_*.py` (수집) | TBD |
| `app/services/scr_*.py` (점수 계산, 순수 함수) | TBD |
| `app/models/`, `app/core/db/`, `pyproject.toml`/`uv.lock` 배포 | TBD |
| `app/templates/`, `app/apis/cmp_pages.py` | TBD |

담당이 아닌 파일은 직접 수정하지 않고 GitHub 이슈로 요청한다.
