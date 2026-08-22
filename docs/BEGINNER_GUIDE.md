# 처음 시작하는 사람을 위한 가이드

`docs/CONTRIBUTING.md`·`CODING_RULES.md`는 에이전트/숙련자용 규칙 원본입니다.
이 문서는 그걸 "손으로 따라 칠 수 있는 순서"로 풀어놓은 것입니다. 막히면 이 문서 →
`docs/TROUBLESHOOTING.md` → 이은호 씨 순으로 물어보세요.

## 0. 설치 & 실행 확인 (30분 목표)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.13
uv sync --group app --group dev
Copy-Item envs\example.local.env .env
uv run uvicorn app.main:app --reload
```

브라우저에서 http://localhost:8000/health → `{"status":"ok"}`가 뜨면 끝입니다.
**`--group ai`는 절대 넣지 마세요** (torch 등 2GB, 안 씀).

## 1. 파일 종류별로 하는 일이 다르다

역할 분담(누가 어떤 파일을 맡을지)은 아직 확정 전입니다. 대신 코드 종류별로 지켜야 할
경계는 정해져 있으니, 어떤 파일을 맡든 아래 구분만 기억하면 됩니다.

| 파일 종류 | 예 | 무엇을 하는 코드인가 |
|---|---|---|
| 수집 (`cmp_*.py`) | `app/services/cmp_openfda.py` | 외부 API 호출 → dict 반환. DB·화면 몰라도 됨 |
| 점수 계산 (`scr_*.py`) | `app/services/scr_index.py` | 숫자 계산만. 사칙연산 함수. I/O 없음 |
| 화면 | `app/templates/*.html`, `app/apis/cmp_pages.py` | Jinja2 화면 + 인라인 SVG 매트릭스 |
| 기반 | `app/models/`, `app/core/db/` | 나머지 전부의 기반 |

**지금 내가 작업 중이 아닌 파일은 직접 고치지 않습니다.** 고칠 일이 생기면 GitHub 이슈로
"이 파일 이렇게 바꿔주세요"라고 요청하세요.

## 2. Git 순서 (매번 이 순서 그대로)

```bash
git checkout dev
git pull origin dev
git checkout -b feature/12-openfda-collector   # 12=이슈 번호
# ... 코드 작성 ...
git add app/services/cmp_openfda.py app/tests/test_cmp_openfda.py
git commit -m "feat(cmp): openFDA 수집 함수 추가"
git push -u origin feature/12-openfda-collector
gh pr create --base dev
```

- 브랜치 이름: `feature/이슈번호-짧은설명`
- 커밋 메시지: `feat(범위): 설명` / `fix(범위): 설명`
- PR은 작게 (파일 1~2개). 커지면 리뷰가 밀리고 충돌이 커집니다
- 절대 하지 않는 것: `git push --force`, `main`/`dev`에 직접 커밋, 남의 브랜치 강제 수정

## 3. 테스트 먼저, 그다음 코드 (TDD)

**순서를 반드시 지키세요: 테스트를 먼저 쓰고, 그 테스트가 실패하는 걸 확인한 다음,
통과하는 코드를 씁니다.** 기대값(정답)은 사람이 손으로 계산해서 정합니다.

### 예시 A — 점수 계산: 가장 쉬운 시작점

```python
# app/tests/test_scr_index.py
from app.services.scr_index import risk_index

def test_risk_index_basic():
    # 손으로 계산: (25*80 + 25*60) / (25+25) = 70.0
    components = {"r1": 80, "r2": 60}
    weights = {"r1": 25, "r2": 25}
    assert risk_index(components, weights) == 70.0

def test_risk_index_ignores_none():
    # r2가 None이면 분자·분모 모두에서 제외 → (25*80)/25 = 80.0
    components = {"r1": 80, "r2": None}
    weights = {"r1": 25, "r2": 25}
    assert risk_index(components, weights) == 80.0
```

```bash
uv run pytest app/tests/test_scr_index.py -v   # 먼저 실패(RED) 확인 — 함수가 없으니까 당연히 실패
```

이제 통과하는 함수를 작성합니다.

```python
# app/services/scr_index.py
def risk_index(components: dict[str, float | None], weights: dict[str, float]) -> float | None:
    num = sum(weights[k] * v for k, v in components.items() if v is not None)
    den = sum(weights[k] for k, v in components.items() if v is not None)
    return num / den if den else None
```

```bash
uv run pytest app/tests/test_scr_index.py -v   # 통과(GREEN) 확인
```

`app/services/scr_*.py`는 표준 라이브러리 외 import 금지, `requests`도 DB도 손대지 않습니다.
이게 규칙에서 가장 검수하기 쉬운 파일입니다 — 계산이 손으로 확인 가능하니까요.

### 예시 B — 수집: API 응답을 dict로

실제 API를 매번 호출하며 테스트하면 느리고 인터넷이 끊기면 실패합니다. 그래서 응답을
한 번 저장해두고 그걸로 테스트합니다.

```python
# app/tests/fixtures/openfda_sample.json  ← 실제 API 응답을 한 번 저장해둔 파일
# app/tests/test_cmp_openfda.py
import json
from pathlib import Path
from app.services.cmp_openfda import parse_openfda_response

def test_parse_openfda_response():
    raw = json.loads(Path("app/tests/fixtures/openfda_sample.json").read_text())
    result = parse_openfda_response(raw)
    assert result["compound_name"] == "amoxicillin"   # 픽스처 파일 안 실제 값으로 채우세요
    assert result["adverse_event_count"] == 12
```

```python
# app/services/cmp_openfda.py
import requests

def fetch_openfda(compound_name: str) -> dict:
    resp = requests.get("https://api.fda.gov/...", params={"search": compound_name}, timeout=10)
    resp.raise_for_status()
    return parse_openfda_response(resp.json())

def parse_openfda_response(raw: dict) -> dict:
    return {
        "compound_name": raw.get("compound_name"),
        "adverse_event_count": raw.get("count"),   # 값이 없으면 None. 0으로 바꾸지 않는다
    }
```

수집 함수는 `requests`만 쓰고, DB나 `app/templates`를 import하지 않습니다. dict를 반환하면 끝 —
그 dict를 DB에 저장하는 건 이은호 씨 코드가 합니다.

### 예시 C — 화면: Jinja2 + 인라인 SVG

```python
# app/apis/cmp_pages.py
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core import config

router = APIRouter()
templates = Jinja2Templates(directory=config.Config().TEMPLATE_DIR)

@router.get("/")
async def matrix_page(request: Request):
    compounds = [{"name": "amoxicillin", "risk": 40, "opportunity": 70}]  # 나중에 DB에서 읽음
    return templates.TemplateResponse(request, "matrix.html", {"compounds": compounds})
```

```html
<!-- app/templates/matrix.html -->
<svg viewBox="0 0 400 400">
  {% for c in compounds %}
  <circle cx="{{ c.opportunity * 4 }}" cy="{{ 400 - c.risk * 4 }}" r="6">
    <title>{{ c.name }} — 위험 {{ c.risk }} / 기회 {{ c.opportunity }}</title>
  </circle>
  {% endfor %}
</svg>
<p style="color:gray">데이터 없음이 회색으로 보이는 항목은 "위험이 없다"는 뜻이 아닙니다.</p>
```

`main.py`에 `app.include_router(cmp_pages.router)`를 추가하면 됩니다. 화면 라우터에는
계산 로직을 넣지 않고, 값은 전부 점수 계산 서비스 함수가 만들어서 넘겨줍니다.

## 4. 검증 (PR 올리기 전에 꼭)

```bash
uv run pytest -v
uv run ruff check app/
uv run ruff format --check app/
```

셋 다 통과해야 PR을 올립니다. 실패하면 에러 메시지를 그대로 복사해서 AI에게 보여주고
"이 에러 고쳐줘"라고 하면 됩니다 — 에러 메시지를 읽지 못해도 괜찮습니다.

## 5. 자주 나는 에러

- `ModuleNotFoundError` → `uv sync --group app --group dev`부터 다시
- `.env` 관련 에러 → `Copy-Item envs\example.local.env .env` 했는지 확인 (심볼릭 링크 아님, 각자 복사본)
- 그 외 → `docs/TROUBLESHOOTING.md`에 증상별로 정리되어 있음, 없으면 이은호 씨에게

## 6. 막히면 (STOP)

AI에게 시키다가 방향이 이상하면 메시지에 `STOP`이라고만 쓰세요. 지금까지 이해한 내용을
요약하고 멈춥니다. 취소가 아니라 "다시 확인" 모드로 바뀌는 것뿐입니다.
