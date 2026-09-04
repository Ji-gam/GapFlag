# SESSION_HANDOFF.md — 다음 세션 인수인계

v1.0 · 작성 2026-08-16 · 이 문서 하나만 읽으면 이전 대화 없이 이어서 작업할 수 있다.
최신 업데이트는 §11(2026-09-05) 참고 — R4 연동, Render 배포.

---

## 0. 30초 요약

| 항목 | 내용 |
|---|---|
| 프로젝트 | **Gap & Flag (갭앤플래그)** — 동물용 의약품 타깃·성분 스크리닝 도구 |
| 한 줄 | 연구 공백(기회)과 위험 신호를 한 화면에서 교차 검증해 **"왜 아무도 이걸 안 했는지"**에 답한다 |
| 소속 | 2026 KU AI Nest AI 창업 실전 프로그램 · 바이오 트랙 |
| 기간 | 2026.8.22 ~ 9.6 (수업 6회 + 수업 외 개발 시간) |
| 팀 | 박정하 · 이은호 · 양민경 · 정보교 (개발 경험자 1명 + 처음 코딩 3명, **전원 바이브코딩**) |
| 저장소 | `D:\Project\Ku_nest\GapFlag` (on-gi-project-template 기반) |
| 현재 단계 | 기획·조사 완료, 코드는 템플릿 + 환경 설정만. **도메인 코드 0줄** |

---

## 1. 확정된 결정

### 1-1. 아이디어 선정 경위

4명이 각자 다른 아이디어를 냈고 두 갈래로 나뉘었다.

- 보호자 축: 박정하(반려동물 이상반응 검색) + 정보교(반려동물 홈케어 가이드)
- 전문가 축: 이은호(신약 레드플래그 지수) + 양민경(동물 연구현황 대시보드)

**팀 회의로 전문가 축(이은호 + 양민경)을 채택**했다. 두 안은 같은 공개 DB를 쓰고, 이은호의 "위험"과 양민경의 "기회"가 2×2의 두 축으로 자연스럽게 합쳐진다.

### 1-2. 확정 사항

| 항목 | 결정 | 비고 |
|---|---|---|
| 팀명 | **갭앤플래그 / Gap & Flag** | Gap=연구 공백(양민경), Flag=레드플래그(이은호). 두 사람이 대등하게 들어감 |
| 저장소명 | `gap-and-flag` | `&`는 URL에 못 씀. 표시명은 `Gap & Flag` |
| 핵심 컨셉 | **기회 × 위험 2×2 매트릭스** | 좌상단 "비어 있는 이유가 있음"이 제품의 핵심 가치 |
| 1차 입력 키 | **성분명(active ingredient)** — 타깃 아님 | §4-1 참고. 가장 중요한 설계 결정 |
| 로컬 DB | SQLite (배포는 MySQL) | 설치 최소화. `docs/MVP_SCOPE.md` §2-2 |
| 화면 | FastAPI + **Jinja2 서버 템플릿** (React 유예) | Node.js 설치 회피. `MVP_SCOPE.md` §2-3 |
| MVP 범위 | **엔드포인트 3개 / 화면 3개** | 늘리지 않는다 |

> **주의: 초기 대화에서 Streamlit + SQLite를 권했다가 철회했다.** 저장소를 열어보니 FastAPI 기반 실무 템플릿이 이미 갖춰져 있었기 때문이다. **Streamlit은 쓰지 않는다.**

---

## 2. 저장소 현재 상태

### 2-1. 템플릿 구성 (on-gi-project-template)

```
app/          FastAPI 백엔드 — apis/v1, dtos, services, repositories, models, core, tests
ai_worker/    RAG·백그라운드 워커 (MVP에서 미사용)
auth_kit/     인증 드롭인 모듈 (main.py에서 주석 처리 = 미사용)
security_kit/ 보안 모듈
frontend/     React + Vite + Tailwind (MVP에서 손대지 않음)
infra/ envs/ scripts/
docs/         AGENTS.md 진입점, CODING_RULES.md, CONTRIBUTING.md, TROUBLESHOOTING.md
```

**반드시 먼저 읽을 문서**: `AGENTS.md`(정책·라우팅 진입점) → `docs/CODING_RULES.md`(계층·네이밍·API 포맷·TDD) → `docs/CONTRIBUTING.md`(브랜치·PR·검증) → `docs/MVP_SCOPE.md`(우리 팀의 유예 결정)

### 2-2. 이번 세션에서 저장소에 적용한 변경

| 파일 | 변경 | 상태 |
|---|---|---|
| `app/core/config.py` | `DATABASE_URL` 필드 추가 (기본 SQLite) | ✅ 적용됨 |
| `app/core/db/databases.py` | 하드코딩 MySQL URL 제거 → `config.DATABASE_URL` | ✅ 적용됨 |
| `app/core/db/migrations/env.py` | 동일 + SQLite `render_as_batch=True` | ✅ 적용됨 |
| `pyproject.toml` | langchain/torch/chroma `ignore_missing_imports` 예외 추가 | ✅ 적용됨 |
| `envs/example.local.env` | `DATABASE_URL` 항목 추가 | ✅ 적용됨 |
| `.gitignore` | `data/` 무시 + `!data/.gitkeep` | ✅ 적용됨 |
| `data/.gitkeep` | 신규 | ✅ 적용됨 |
| `docs/MVP_SCOPE.md` | 신규 — 유예 항목 7개와 되돌리는 조건 | ✅ 적용됨 |
| **`.github/workflows/ci.yml`** | `uv sync --all-groups` → `--group app --group dev` | ⚠️ **미적용 — 수동 수정 필요** |

> `ci.yml`은 보호된 파일이라 도구로 쓸 수 없다. **백엔드 잡의 Install Dependencies 한 줄만 바꾸면 된다.** 그대로 두면 매 PR마다 torch(수 GB)를 받아 CI가 느려진다.

### 2-3. 팀원 셋업 (설치 3개)

Git(또는 GitHub Desktop) · uv · 에디터+AI 도구. **Python·Node.js·MySQL·Docker 설치 불필요.**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.13
uv sync --group app --group dev      # ai 그룹은 절대 넣지 않는다
Copy-Item envs\example.local.env .env
uv run uvicorn app.main:app --reload
```

`http://localhost:8000/health` → `{"status":"ok"}` 이면 완료. Docker는 이은호만, 배포 직전에.

---

## 3. 시장조사 핵심 수치 (재조사 불필요)

조사일 2026-08-16. 전체는 `GapFlag_시장조사_보고서.pdf` / `gapflag-market.html`.

### 3-1. 시장 규모

| 항목 | 수치 | 출처 |
|---|---|---|
| 글로벌 동물약 상위 20개사 매출 | **USD 386억** (2024) | HealthforAnimals ✅ |
| 글로벌 동물약 시장 | USD 687억~702억 (2025) | 리서치사 ⚠️ 신뢰도 낮음 |
| 한국 동물약 시장 | **1조 5,162억 원** (+10.5%, 2025) | 한국동물약품협회 ✅ |
| 글로벌 동물약 R&D 총지출 | **USD 30억/년** | HealthforAnimals ✅ |
| R&D 집약도 | 매출의 **7~8%** (인체 제약 20~27%) | Zoetis 7.4%, Elanco 7.8% ✅ |
| 유럽 동물약 기업 수 | **130개사 이상**(SME 100+) | AnimalhealthEurope ✅ |
| AI in Animal Health | USD 18억, **CAGR 18.9%** | Grand View ⚠️ |
| AI 신약개발 | USD 23억~199억 (리서치사 간 8배 차이) | ⚠️ **반드시 범위로 인용** |

**TAM/SAM/SOM (전부 추정)**
- TAM ≈ USD 4,000만~5,000만/년 — 동물약 R&D 지출 30억 × 정보SW 비중 1.5%(추측)
- SAM ≈ **USD 180만~250만/년 (약 25억~35억 원)** — 시장이 작다는 점을 팀이 직시해야 함
- SOM ≈ 연 1,000만~5,000만 원 (국내 3년)

### 3-2. 데이터 소스 (전부 확인 완료)

| 소스 | 용도 | 조건 |
|---|---|---|
| **openFDA ADAE** | 위험 R2 동물 이상반응 | 무료 REST, 키 발급 시 일 12만 요청. **130만 건** |
| **Open Targets** | 위험 R1 사람 임상 중단 사유 | GraphQL, 무료, **CC0(상업 이용 가능)** |
| **FDA Green Book** | 위험 R3 승인·철회 + 특허·독점기간 / 기회 O3 미승인 | 무료. **공식 API 없음 — 파일 파싱 필요** |
| **EPO OPS** | 위험 R4 특허 밀집도 | 무료 주 3.5GB, 무제한 연 €2,800. **OAuth 키 발급 필요** |
| **Europe PMC** | 기회 O1 문헌 희소성 | 무료·인증 불필요. 레이트 리밋 미공개 → 캐시 필수 |
| ClinicalTrials.gov | 기회 O2 임상 부재 | 무료 v2. 동물 임상은 등록 의무 없음 → 가중치 낮게 |
| ~~EMA EudraVigilance Vet~~ | — | **공식 API 못 찾음. MVP 제외** |

### 3-3. 경쟁 지형

- **같은 콘셉트의 상용 제품 없음.** Cortellis·PharmaPendium·Citeline은 인체 전용, Open Targets·Pharos는 무료지만 **종 축 없음**, VetCompass 등 수의 데이터는 진료 역학이라 타깃 발굴 불가.
- 가격: Clarivate 계약 중간값 연 $175,931 / PatSnap Life Sci Pro $400월(공식) / Euretos Academic €1,200년 / **조사 12개 도구 중 정가 공개는 4개뿐**
- **최대 위협**: Absci–Invetx 제휴 (인체 AI 신약설계 플랫폼의 수의 확장), 대형사 사내 툴(존재 여부 알 수 없음)

### 3-4. 핵심 문헌 근거 (발표에서 가장 강한 무기)

> **Court MH (2013), Vet Clin North Am Small Anim Pract**
> "인체 데이터는 평가된 대부분의 약물에서 개·고양이의 소실 반감기 예측에 **부적합했다**."

- 고양이 UGT1A6 = 위유전자, UGT1A9 결핍 → 글루쿠론산 포합 안 됨
- aspirin 반감기 고양이 22시간 vs 개 4.5시간 / propofol 8.8시간 vs 2.4시간
- acetaminophen: 고양이는 NAT2도 없어 간독성이 아닌 **메트헤모글로빈혈증**
- 관련: Shrestha et al. (2011) PLoS ONE, Schneider et al. (2018) CPT:PSP

**대비되는 사실**: FDA 최근 5년 승인 동물 신약은 일부를 제외하면 **전부 인체 임상 이력 보유**(바이오타임즈 2025.2). 국내도 대웅펫·지엔티파마·동국제약·유한양행·종근당바이오 전부 인체약 파생.
→ **관행과 과학의 이 간극이 제품이 메우는 자리다.**

### 3-5. 확인하지 못한 것

- 국내 동물약 제조업체 수 (공공데이터포털 파싱으로 실측 가능)
- 글로벌 동물약 개발 기업 총수 (Green Book sponsor 파싱으로 실측 가능)
- **동물약 개발 실패율·중단 사유 통계 — 존재하지 않는 것으로 보임**
- 상용 도구 12개 중 8개의 실제 구독료
- **고객 인터뷰 0건** ← 가장 큰 빈칸

---

## 4. 제품 설계

### 4-1. 조인 키 — 가장 중요한 설계 결정

**1차 키는 `성분명(active ingredient)`이다. 타깃(유전자)이 아니다.**

Open Targets는 타깃 중심이고 Green Book·openFDA는 성분 중심이라, 타깃을 1차 키로 잡으면 매핑 검증에만 1~2주가 걸린다. 성분명을 축으로 잡으면 모든 소스가 바로 붙는다.

```
1차 키 : ingredient_name (소문자 정규화)
2차 키 : species ∈ {dog, cat}
파생   : target_symbol ← ChEMBL 경유, Open Targets 조회 시에만
```

성분명 표기 흔들림은 **동의어 사전을 수작업 관리**한다(30~50건 규모라 자동화보다 빠르다).

### 4-2. 지수 산식

| ID | 구성요소 | 환산식 |
|---|---|---|
| R1 | 임상 중단 이력 | 독성 100 · 효능부족 60 · 사업적 20 · 없음 0 |
| R2 | 동물 이상반응 (건수 n) | `min(100, 25 × log₁₀(n+1))` |
| R3 | 승인·철회 이력 | 철회 100 · 승인 유지 20 · 기록 없음 NULL |
| R4 | 특허 밀집도 (패밀리 p) | `min(100, 30 × log₁₀(p+1))` |
| O1 | 문헌 희소성 (논문 m) | `max(0, 100 − 30 × log₁₀(m+1))` |
| O2 | 임상 부재 (시험 t) | t=0 → 100 · t≥1 → `max(0, 100 − 40×log₁₀(t+1))` |
| O3 | 미승인 | 미승인 100 · 승인 0 |

```
위험 지수 = Σ(wᵢ×Rᵢ) / Σ(wᵢ)     NULL 구성요소는 분자·분모 모두에서 제외
기회 지수 = Σ(wⱼ×Oⱼ) / Σ(wⱼ)
커버리지 = 값이 있는 구성요소 수 / 전체
```

기본 가중치 — 위험 R1~R4 각 25 / 기회 O1 40, O2 30, O3 30
계수(25·30·40)는 **초기 가정**이다. 4분면에 고르게 흩어지지 않으면 조정하고 이력을 남긴다.

**사분면** (기준선 각 50)

| | 위험 ≥50 | 위험 <50 |
|---|---|---|
| **기회 ≥50** | **비어 있는 이유가 있음** ← 핵심 | **우선 검토** |
| **기회 <50** | 회피 | 경쟁 구간 |

### 4-3. 타협 불가 원칙

- **데이터 없음은 `None`. 절대 0으로 치환하지 않는다.** 점수 컬럼 전부 nullable.
  (0점 = 확인했고 위험 없음 / NULL = 확인하지 못함)
- NULL은 계산에서 제외하고 **커버리지 %를 함께 표시**한다.
- 화면에서 "데이터 없음"은 회색 + **"위험이 없다는 뜻이 아닙니다"** 문구.
- 원본 API 응답(raw JSON)을 DB에 함께 저장한다.
- 화면은 DB만 읽는다. 화면에서 외부 API를 직접 호출하지 않는다.
- 모든 화면 하단: **"본 도구는 참고용이며 의료·규제 판단을 대신하지 않습니다."**

### 4-4. 파일 배치 (도메인 코드 CMP / SRC / SCR)

```
app/models/cmp_models.py           Compound / CompoundScore / CompoundEvidence / SpeciesAlert
app/repositories/cmp_repository.py AsyncSession 쿼리만
app/services/cmp_service.py        조회 조합
app/services/src_openfda_service.py 외부 API 호출 (Service가 담당 — CODING_RULES §1 허용)
app/services/src_greenbook_service.py / src_europepmc_service.py
app/services/src_opentargets_service.py / src_epo_service.py
app/core/utils/scr_normalize.py    순수 함수 (I/O 없음)
app/core/utils/scr_index.py        지수 계산
app/dtos/cmp_dtos.py
app/apis/cmp_pages.py              HTML 페이지 (Jinja2) — /api/v1 아래 아님
app/templates/                     Jinja2 템플릿
scripts/build_cache.py             수집 배치 (수동 실행)
```

### 4-5. 화면 3개 + 소개

| ID | 화면 | 우선순위 |
|---|---|---|
| S1 | 2×2 매트릭스 (기회 × 위험) — **인라인 SVG로 렌더링**, 차트 라이브러리 없음 | P0 |
| S2 | 성분 상세 + 근거 카드 (출처·요약·원문 링크) | P0 |
| S3 | 후보 비교 | P1 (잘라도 됨) |
| S0 | 소개 · 데이터 출처 · **산식 전문 공개** | P1 |

### 4-6. 잘라내는 순서

① S3 비교 → ② 실시간 조회 → ③ 특허(EPO) 구성요소 → ④ Green Book(R3·O3)

**절대 버리지 않는 것**: 2×2 매트릭스 / 근거 카드와 원문 링크 / "데이터 없음" 회색 표시

미완성 구성요소는 `CODING_RULES.md` §8 **Tier2 stub 패턴**으로 처리한다. DTO·Router는 최종 형태로 두고 Service 내부만 `None` 반환. §4-3의 NULL 설계가 그대로 안전장치가 된다.

---

## 5. 역할 분담

| 사람 | 담당 | 필요한 지식 |
|---|---|---|
| **이은호** (경험자) | `models/` `repositories/` `core/db/` Alembic 배포 `pyproject.toml` `uv.lock` | 프레임워크 |
| **박정하** | `services/src_*` · `tests/fixtures/` | requests와 dict |
| **양민경** | `core/utils/scr_*` · `tests/test_scr_*` | 함수와 사칙연산 |
| **정보교** | `apis/cmp_pages.py` · `templates/` · SVG 매트릭스 | HTML/CSS |

- 남의 파일은 직접 고치지 않고 GitHub 이슈로 요청
- **Alembic 리비전은 이은호만 생성** (병렬 생성 시 head 갈라짐)
- **스키마는 2회차까지 동결**
- 매 회차 시작에 각자 자기 파일을 **2분 설명** (바이브코딩 이해 검증)

---

## 6. 지금까지 만든 산출물

저장소 안:
- `docs/MVP_SCOPE.md` — 유예 항목 7개, 설치 목록, 도메인 코드, 파일 배치, 소유권
- `docs/SESSION_HANDOFF.md` — 이 문서

저장소 밖 (팀 공유용, 필요하면 `docs/`로 옮길 것):
- `GapFlag_시장조사_보고서.pdf` (8p) / `gapflag-market.html` — 7단계 시장조사 + 출처 22건
- `GapFlag_문제해결_분석.pdf` (7p) — AS-IS/TO-BE/GAP/6M/5Why/대책
- `GapFlag_비즈니스모델캔버스.pdf` (1p) — BMC 9블록
- `gapflag-requirements.md` — MVP 요구사항 정의서 v0.1 (화면·스키마·산식·AC 12개)
- `tech-stack-guide.md` / `CLAUDE.md` — 초기 스택 검토 문서 ⚠️ **Streamlit 전제라 현재는 무효**
- `KU_AI_Nest_팀_아이디어_비교표.pdf` — 4인 아이디어 비교

---

## 7. 다음에 할 일 (우선순위 순)

### 즉시

1. **`ci.yml` 한 줄 수정** (§2-2 미적용 항목)
2. **4명 전원 `uv sync` + `uvicorn` 실행 확인** — 여기서 막히면 최우선 과제
3. ~~EPO OPS 개발자 키 신청~~ → **PatentsView로 전환됨(§11)**. USPTO ODP 신원인증(ID.me) 대기 중 — 급하면 시간 날 때 진행, 데모는 R4 NULL로도 문제없음
4. **대상 성분 30~50건 확정** → `data/seed_compounds.csv` 커밋
   - 개·고양이 대상, 항체·단백질 의약품 우선
   - **4개 사분면에 고르게 분포하도록** 선정 (한쪽에 몰리면 도구가 작동하는지 못 보여줌)
   - 종간 대사 사례(carprofen, propofol, acetaminophen, aspirin) 반드시 포함

### 2회차까지

5. `cmp_models.py` 4개 테이블 + Alembic 초기 리비전 → **스키마 동결**
6. `scr_*` 순수 함수 + 손으로 계산한 기대값 테스트 5건
7. `src_openfda_service.py` + `tests/fixtures/`

### 검증이 필요한 것

8. **동물약 개발 실무자 3~5명 인터뷰** — 이번 조사의 가장 큰 빈칸. 문제 크기와 지불 의사를 동시에 검증
9. Green Book 허가권자 파싱 → 미국 잠재 고객 수 실측 (MVP 코드 재사용)
10. 공공데이터포털 허가 현황 파싱 → 국내 업체 수 실측

---

## 8. 미결정 사항

| # | 항목 | 기한 |
|---|---|---|
| OI-01 | 대상 성분 최종 목록 | 1회차 |
| OI-02 | 항체·단백질 의약품 우선 여부 확정 | 1회차 |
| OI-03 | ~~배포처 결정 및 빈 앱 배포~~ | ✅ 해결(§11) — Render 무료, https://gapflag.onrender.com |
| OI-04 | 성분명 동의어 사전 초안 | 2회차 |
| OI-05 | §4-2 정규화 계수 실측 조정 | 3회차 |
| OI-06 | 사분면 라벨 한글 최종 문구 | 3회차 |
| OI-07 | 전북 클러스터·한국동물약품협회 접촉 여부 | 미정 |

---

## 9. 다음 세션 시작 프롬프트 예시

```
Gap & Flag 프로젝트를 이어서 진행한다.
D:\Project\Ku_nest\GapFlag 폴더가 연결되어 있고,
docs/SESSION_HANDOFF.md 와 docs/MVP_SCOPE.md 를 먼저 읽어라.

오늘 할 일: [예) cmp_models.py 4개 테이블과 Alembic 초기 리비전 작성]
```

**주의할 것**
- Streamlit·pandas·plotly·async 금지 판단은 **초기 대화의 오래된 결론이다.** 현재는 FastAPI 템플릿을 쓰므로 **async는 필수**이고, Streamlit은 쓰지 않는다.
- `uv.lock`에 있는 패키지만 쓴다. 새 의존성 추가 금지.
- `pandas`·`plotly`는 lock에 없다. 차트는 인라인 SVG.
- AI가 SQLAlchemy 1.x 문법(`session.query()`)이나 Pydantic v1(`@validator`)을 쓰지 않는지 확인할 것. 이 저장소는 **SQLAlchemy 2.0 + Pydantic v2**다.

---

## 10. 발표·심사 대비 메모

**가장 강한 한 장면** — Court(2013) 인용문을 띄우고 "업계는 이미 인체 데이터를 전용하는데, 문헌은 그게 부적합하다고 말한다"로 문제 정의를 끝낸다.

**반드시 나올 질문 세 개와 답**

1. *"왜 70점인가?"* → 총점만 보여주지 않는다. 구성요소·가중치·산식을 전부 공개하고 사용자가 슬라이더로 조정한다.
2. *"시장이 너무 좁지 않나?"* → 인정한다. SAM 추정 25억~35억 원. 그래서 고객을 "동물약 회사"가 아니라 **"인체 자산을 동물로 확장하려는 모든 바이오텍"**으로 정의했고, 장기 해자는 도구가 아니라 **축적되는 데이터**다.
3. *"경쟁사가 하면 되지 않나?"* → 대형 벤더는 인체 시장이 100배라 동물 쪽에 안 온다. 공공 도구는 인간 유전체 기반이라 종 축 추가가 확장이 아니라 재설계다.

**절대 하지 말 것** — 수치를 단정하기. AI 신약개발 시장은 리서치사별로 8배 차이가 난다. 항상 범위로 말한다.

---

## 11. 2026-09-05 세션 업데이트 — R4 연동 · Render 배포

### R4(특허 밀집도) 연동

EPO OPS는 OAuth2 승인 대기가 필요해서, **PatentsView Search API로 전환**했다.

- `app/services/src_patentsview_service.py` 신규 (기존 `src_*.py`와 동일 패턴)
- `scr_normalize.r4_patent_density()` 추가, `build_cache.py`에 배선
- 그런데 PatentsView도 2025년 USPTO Open Data Portal(ODP)로 흡수되면서 **ID.me 신원인증**(정부 신분증 업로드)이 필요해졌다 — 결국 EPO OPS와 비슷한 진입장벽. 지금은 `PATENTSVIEW_API_KEY`가 비어 있어 R4는 NULL로 남아 있다(설계상 정상 — 위험지수 커버리지 75%로 표시됨).
- 이은호 씨가 ID.me 인증 마치고 키 받으면 `.env`에 `PATENTSVIEW_API_KEY` 넣고 `uv run python -m scripts.build_cache` 재실행하면 채워진다.
- PR: [#35](https://github.com/Ji-gam/GapFlag/pull/35)

### 배포 — Render 무료 티어

3일짜리 데모용으로 **Render(Docker 웹서비스, Free 플랜)**에 배포했다.

- URL: **https://gapflag.onrender.com**
- Railway는 1회성 $5 트라이얼 크레딧 소진 후 카드 필요 → 제외. Render 무료는 크레딧 소진형이 아니라 매달 갱신되는 flat 무료 플랜(카드 불필요)이라 채택
- 무료 티어는 15분 미접속 시 슬립되고 디스크가 초기화됨 → MySQL 대신 **SQLite + 컨테이너 기동할 때마다 `build_cache.py` 재수집**하는 방식 채택(`app/Dockerfile` CMD). 재기동마다 1~2분 정도 로딩 필요
- `aiosqlite`가 원래 `dev` 그룹에만 있어 배포 이미지(MySQL 드라이버 `asyncmy`만 있음)가 SQLite로 못 떴던 문제 발견 → 이슈 [#34](https://github.com/Ji-gam/GapFlag/issues/34)로 요청, 승인받아 `app` 그룹에도 추가
- PR: [#36](https://github.com/Ji-gam/GapFlag/pull/36)
- 로컬 `docker build` + `docker run`으로 Render와 동일한 콜드스타트 시퀀스(마이그레이션 → 35개 성분 재수집 → 서버 기동)를 미리 검증하고 배포함

### 남은 것

- **발표 직전에 한 번 미리 접속해서 깨워둘 것** (슬립 상태면 첫 방문자가 1~2분 대기)
- 계속 안 잠들게 하려면 [UptimeRobot](https://uptimerobot.com) 같은 무료 핑 서비스로 10분마다 접속 — 제안만 하고 아직 설정 안 함
- 데모 끝나면(9/6 이후) Render 서비스 삭제할 것 — 계속 켜둘 이유 없음
- R4는 ID.me 인증 끝나야 채워짐 — §7 3번 항목 참고
