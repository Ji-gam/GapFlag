# SESSION_HANDOFF.md — 다음 세션 인수인계

v1.2 · 작성 2026-08-16, 갱신 2026-09-01 → 2026-09-04 · 이 문서 하나만 읽으면 이전 대화 없이 이어서 작업할 수 있다.

**v1.2에서 바뀐 것**: v1.1(09-01) 이후 O2(ClinicalTrials.gov 임상 부재) 수집 서비스가
[PR #20](https://github.com/Ji-gam/GapFlag/pull/20)으로 머지됐다. 기회지수 커버리지가
33% → **66.7%**로 올랐고 실측 분포도 갱신됐다. §0(요약)·§2(저장소 상태)·§3-2(데이터
소스 표)·§4-2(산식 표)·§7(다음 할 일)을 갱신했다. §1·§3-1/3-3~3-5·§5·§10은 그대로 유효.

---

## 0. 30초 요약

| 항목 | 내용 |
|---|---|
| 프로젝트 | **Gap & Flag (갭앤플래그)** — 동물용 의약품 타깃·성분 스크리닝 도구 |
| 한 줄 | 연구 공백(기회)과 위험 신호를 한 화면에서 교차 검증해 **"왜 아무도 이걸 안 했는지"**에 답한다 |
| 소속 | 2026 KU AI Nest AI 창업 실전 프로그램 · 바이오 트랙 |
| 기간 | 2026.8.22 ~ 9.6 (발표까지 2일 남음, 2026-09-04 기준) |
| 팀 | 박정하 · 이은호 · 양민경 · 정보교 (개발 경험자 1명 + 처음 코딩 3명, **전원 바이브코딩**) |
| 저장소 | `D:\Project\Ku_nest\GapFlag` (on-gi-project-template 기반), GitHub `Ji-gam/GapFlag` |
| 현재 단계 | **화면 동작함.** DB 모델·수집 서비스 5종(R1/R2/R3/O1/O2)·전체 성분 산점도 매트릭스·근거 카드까지 실제로 켜서 확인 가능. 기회지수 커버리지 66.7%. R4(EPO)·O3 미수집, 시드 성분 34건은 초안(팀 검수 전) |

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
| DB | **FastAPI가 서버에서 직접 렌더링하는 SSR 구조** — 로컬 SQLite (배포는 MySQL) | 별도 프론트엔드/API 분리 없음. `frontend/`(React)는 MVP 기간 미사용 |
| 화면 | FastAPI + **Jinja2 서버 템플릿** | Node.js 설치 회피. `MVP_SCOPE.md` §2-3 |
| MVP 범위 | **엔드포인트 3개 / 화면 3개** | 늘리지 않는다 |

> **주의: 초기 대화에서 Streamlit + SQLite를 권했다가 철회했다.** 저장소를 열어보니 FastAPI 기반 실무 템플릿이 이미 갖춰져 있었기 때문이다. **Streamlit은 쓰지 않는다.**
>
> **주의 2: 이 프로젝트에 "프론트엔드"는 따로 없다.** FastAPI 라우터(`app/apis/cmp_pages.py`)가
> DB를 조회해서 Jinja2 템플릿(`app/templates/`)으로 HTML을 직접 그려서 응답한다. 브라우저는 완성된
> HTML을 받을 뿐 JSON API를 호출하는 JS가 없다. `frontend/`(React+Vite) 폴더는 템플릿에 원래 있던
> 것인데 MVP 기간엔 안 쓰기로 했다 — 그래서 `frontend`에서 `npm run dev`가 안 되는 건 정상이다.

---

## 2. 저장소 현재 상태 (2026-09-04 기준)

### 2-1. 도메인 코드 — 실제로 구현·동작함

```
app/models/cmp_models.py           Compound / CompoundScore / CompoundEvidence / SpeciesAlert  ✅
app/repositories/cmp_repository.py AsyncSession 쿼리 (search, get, upsert, list_scores)         ✅
app/services/cmp_service.py        DB 조회 조합 + mock 폴백                                     ✅
app/services/cmp_mock.py           마이그레이션 전 폴백용 고정 데이터 1건                        ✅
app/services/src_openfda_service.py       R2 동물 이상반응 (openFDA ADAE)                       ✅
app/services/src_opentargets_service.py   R1 사람 임상 중단 이력 (Open Targets)                  ✅
app/services/src_greenbook_service.py     R3 자발적 승인철회 (FDA Green Book, xlrd 파싱)         ✅
app/services/src_europepmc_service.py     O1 문헌 희소성 (Europe PMC)                            ✅
app/services/src_clinicaltrials_service.py O2 사람 임상시험 부재 (ClinicalTrials.gov v2)         ✅ NEW
app/core/utils/scr_normalize.py    구성요소별 0~100 환산 함수 (순수 함수, o2_clinical_absence 포함) ✅
app/services/scr_score.py          위험·기회 지수 계산 (NULL 제외, 커버리지 계산)                 ✅
app/apis/cmp_pages.py              GET / , GET /matrix , GET /compound/{ingredient}             ✅
app/templates/                     base.html, search.html, matrix.html, detail.html             ✅
scripts/build_cache.py             CSV 읽어 5종 API 순차 수집 → DB 저장 (수동 실행)              ✅
data/seed_compounds.csv            대상 성분 34건 — **초안, 팀 검수 전** (OI-01 미확정)          ⚠️
```

**아직 없는 것**: R4(EPO OPS 특허), O3(Green Book 미승인 여부) 수집 서비스. 산식이 NULL을
견디도록 설계돼 있어 화면은 정상 동작한다.

**O3를 의도적으로 보류한 이유**: Green Book "승인 목록에 없음"을 곧바로 100점(미승인 확정)으로
단정하면 CLAUDE.md의 타협 불가 원칙("데이터 없음은 None, 절대 0/확정값으로 치환 안 함")과
충돌한다. 종(dog/cat)별로 승인 여부가 갈릴 수 있어 Green Book의 별도 섹션(활성 성분 목록)까지
파싱해 종별로 조인해야 정확한데, 그 작업량이 발표(9/6)까지 남은 시간 대비 리스크가 크다고
판단해 미룸.

### 2-2. O2(ClinicalTrials.gov) 수집 — 이번 세션 추가

- `src_clinicaltrials_service.fetch_trial_count(ingredient_name)` — 성분명만으로 조회.
  **species 무관**(R1/R2/R3와 동일 패턴, 사람 임상 등록부라 종 개념이 없음. O1만 종별 검색어 사용).
- API: `GET https://clinicaltrials.gov/api/v2/studies?query.intr=<성분>&countTotal=true&pageSize=1&fields=NCTId&format=json`
  → `{"totalCount": N}`. 매칭 0건도 HTTP 200(openFDA와 달리 404 특례 불필요).
  `fields=NCTId` 없으면 study 1건의 전체 프로토콜이 딸려와 raw_json이 비대해짐 — 주의.
- `scr_normalize.o2_clinical_absence(count)`: `t=0 → 100`, `t≥1 → max(0, 100 − 40·log₁₀(t+1))`.
- `build_cache.py`에 R1~R3/O1과 동일한 4단계 블록(fetch → normalize → upsert_evidence → risk/opportunity dict)으로 연결.
- DB 스키마 변경 없음 (`compound_evidences.component_key`가 자유 문자열이라 새 컬럼·리비전 불필요).
- **[PR #20](https://github.com/Ji-gam/GapFlag/pull/20)** `feature/src-clinicaltrials-o2` → `dev`, 2026-09-01 머지 완료.

### 2-3. 재수집 결과 (2026-09-04, `data/gapflag.db` 실측)

- 35행(성분×종 조합) 전부 **기회지수 커버리지 66.7%**(O1+O2 / 전체 3개 중 2개)로 동일하게 상승 (이전 33.3%)
- 위험지수 범위 19.2~81.6, 기회지수 범위 0.0~70.9 — v1.1(09-01) 시점 "0~55에 몰림"에서 상단으로 퍼짐
- 예: frunevetmab·bedinvetmab 같은 항체 성분이 사람 임상이 없어 기회지수 상단으로 이동 —
  좌상단 "비어 있는 이유가 있음" 사분면에 점이 생기기 시작함(정확한 개수는 `/matrix` 확인 필요)

### 2-4. `/matrix` 화면 — 성분 1개 점이 아니라 전체 산점도

v1.0 작성 시점엔 없었던 화면(PR #18에서 추가). DB에 저장된 **모든 성분·종 조합을 한 번에
산점도로** 그린다(`cmp_repository.list_scores` → `cmp_service.list_matrix_points` →
`matrix.html`의 SVG 루프). 특정 성분 하이라이트(빨간 원), 지수 NULL 조합은 매트릭스 아래
회색 목록으로 별도 표시("위험이 없다는 뜻이 아닙니다"). 점 클릭 → 근거 카드 이동.

### 2-5. Alembic / 테스트

- Alembic 리비전 1개 존재(`f84742b34aad_add_compound_cmp_models.py`), 스키마 동결 중
- `app/tests/` 테스트 **36개**(기존 30 + O2 신규 6: 서비스 3건 + 정규화 3건), 전부 통과.
  `app/tests/fixtures/`에 저장된 API 응답으로 테스트 — 실 API 호출 없음

### 2-6. 팀원 셋업 (설치 3개)

Git(또는 GitHub Desktop) · uv · 에디터+AI 도구. **Python·Node.js·MySQL·Docker 설치 불필요.**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.13
uv sync --group app --group dev      # ai 그룹은 절대 넣지 않는다
Copy-Item envs\example.local.env .env
uv run alembic upgrade head
uv run python -m scripts.build_cache  # 34개 성분 수집 (몇 분 걸림)
uv run uvicorn app.main:app --reload
```

`http://localhost:8000/matrix` 에서 산점도가 보이면 완료. Docker는 이은호만, 배포 직전에.

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

| 소스 | 용도 | 조건 | 수집 상태 |
|---|---|---|---|
| **openFDA ADAE** | 위험 R2 동물 이상반응 | 무료 REST, 키 발급 시 일 12만 요청. **130만 건** | ✅ 구현됨 |
| **Open Targets** | 위험 R1 사람 임상 중단 사유 | GraphQL, 무료, **CC0(상업 이용 가능)** | ✅ 구현됨 |
| **FDA Green Book** | 위험 R3 승인·철회 + 특허·독점기간 / 기회 O3 미승인 | 무료. **공식 API 없음 — 파일 파싱 필요** | ✅ R3 구현됨, O3 **의도적 보류**(§2-1) |
| **EPO OPS** | 위험 R4 특허 밀집도 | 무료 주 3.5GB, 무제한 연 €2,800. **OAuth 키 발급 필요** | ⏳ 가입 완료, 승인 대기 중. 코드 미착수 |
| **Europe PMC** | 기회 O1 문헌 희소성 | 무료·인증 불필요. 레이트 리밋 미공개 → 캐시 필수 | ✅ 구현됨 |
| **ClinicalTrials.gov** | 기회 O2 임상 부재 | 무료 v2, 인증 불필요. 종 개념 없음(사람 임상 등록부) | ✅ 구현됨 (2026-09-01, PR #20) |
| ~~EMA EudraVigilance Vet~~ | — | **공식 API 못 찾음. MVP 제외** | — |

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

성분명 표기 흔들림은 **동의어 사전을 수작업 관리**한다(30~50건 규모라 자동화보다 빠르다). 아직
착수 전 — OI-04.

### 4-2. 지수 산식

| ID | 구성요소 | 환산식 | 수집 상태 |
|---|---|---|---|
| R1 | 임상 중단 이력 | 독성 100 · 효능부족 60 · 사업적 20 · 없음 0 | ✅ |
| R2 | 동물 이상반응 (건수 n) | `min(100, 25 × log₁₀(n+1))` | ✅ |
| R3 | 승인·철회 이력 | 철회 100 · 없음 0(기록 있으면 100, 없으면 0으로 이진화됨 — 원래 3단계 설계는 실측 데이터로 재현 불가) | ✅ |
| R4 | 특허 밀집도 (패밀리 p) | `min(100, 30 × log₁₀(p+1))` | ❌ EPO 대기 |
| O1 | 문헌 희소성 (논문 m) | `max(0, 100 − 30 × log₁₀(m+1))` | ✅ |
| O2 | 임상 부재 (시험 t) | t=0 → 100 · t≥1 → `max(0, 100 − 40×log₁₀(t+1))` | ✅ (09-01) |
| O3 | 미승인 | 미승인 100 · 승인 0 | ❌ 의도적 보류(§2-1) |

```
위험 지수 = Σ(wᵢ×Rᵢ) / Σ(wᵢ)     NULL 구성요소는 분자·분모 모두에서 제외
기회 지수 = Σ(wⱼ×Oⱼ) / Σ(wⱼ)
커버리지 = 값이 있는 구성요소 수 / 전체
```

기본 가중치 — 위험 R1~R4 각 25 / 기회 O1 40, O2 30, O3 30
계수(25·30·40)는 **초기 가정**이다. O2 추가 후 실측(35건, 2026-09-04): 위험지수 19.2~81.6,
기회지수 0.0~70.9로 상단까지 퍼짐(v1.1 시점엔 "0~55에 몰림"이었음). O3까지 채워지면 재분포될
가능성 있음. 4분면에 고르게 흩어지지 않으면 조정하고 이력을 남긴다.

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

### 4-4. 파일 배치 (도메인 코드 CMP / SRC / SCR) — 실제 구현과 대조

```
app/models/cmp_models.py           ✅ Compound / CompoundScore / CompoundEvidence / SpeciesAlert
app/repositories/cmp_repository.py ✅ AsyncSession 쿼리만
app/services/cmp_service.py        ✅ 조회 조합
app/services/src_openfda_service.py ✅ / src_greenbook_service.py ✅ / src_europepmc_service.py ✅
app/services/src_opentargets_service.py ✅ / src_clinicaltrials_service.py ✅ NEW
app/services/src_epo_service.py ❌ (EPO 키 대기 중, 아직 파일 없음)
app/core/utils/scr_normalize.py    ✅ 순수 함수 (I/O 없음), o2_clinical_absence 포함
app/services/scr_score.py          ✅ 지수 계산 (계획 문서는 core/utils/scr_index.py로 적었으나
                                       실제는 app/services/scr_score.py — 경로가 다르니 참고할 것)
app/dtos/cmp_dtos.py               미사용 (템플릿에 dict로 직접 전달 중)
app/apis/cmp_pages.py              ✅ HTML 페이지 (Jinja2) — /api/v1 아래 아님
app/templates/                     ✅ base/search/matrix/detail.html
scripts/build_cache.py             ✅ 수집 배치 (수동 실행, CSV 입력, 5종 API)
```

### 4-5. 화면 3개 + 소개

| ID | 화면 | 우선순위 | 상태 |
|---|---|---|---|
| S1 | 2×2 매트릭스 (기회 × 위험) — **인라인 SVG로 렌더링**, 차트 라이브러리 없음 | P0 | ✅ 전체 산점도로 구현됨 |
| S2 | 성분 상세 + 근거 카드 (출처·요약·원문 링크) | P0 | ✅ 구현됨 |
| S3 | 후보 비교 | P1 (잘라도 됨) | ❌ 미착수 |
| S0 | 소개 · 데이터 출처 · **산식 전문 공개** | P1 | ❌ 미착수 |

### 4-6. 잘라내는 순서

① S3 비교 → ② 실시간 조회 → ③ 특허(EPO) 구성요소 → ④ O3(Green Book 미승인)

**절대 버리지 않는 것**: 2×2 매트릭스 / 근거 카드와 원문 링크 / "데이터 없음" 회색 표시 —
**전부 지금 화면에 살아있다.**

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
- `docs/REQUIREMENTS(요구사항정의서).md` — SRS v1.0 (2026-08-29). **R3/O2 구현이 SRS 작성
  이후 들어갔으므로 문서가 코드보다 뒤처져 있음** — 실제로는 R1/R2/R3/O1/O2 5개 구현됨
- `docs/BEGINNER_GUIDE.md` — 초보 3명용 셋업 가이드. 예시 파일명이 옛 명명 규칙이라 실제
  `src_*`/`scr_normalize.py`와 다름, 참고 시 주의
- `data/seed_compounds.csv` — 대상 성분 34건 초안 (**팀 검수 전**)
- `docs/SESSION_HANDOFF.md`(v1.0) → `docs/SESSION_HANDOFF_1.md`(v1.1) → 이 문서(v1.2) — 세션
  인수인계 스냅샷. 과거 버전도 지우지 말고 그대로 둔다(이력 추적용)

저장소 밖 (팀 공유용, 필요하면 `docs/`로 옮길 것):
- `GapFlag_시장조사_보고서.pdf` (8p) / `gapflag-market.html` — 7단계 시장조사 + 출처 22건
- `GapFlag_문제해결_분석.pdf` (7p) — AS-IS/TO-BE/GAP/6M/5Why/대책
- `GapFlag_비즈니스모델캔버스.pdf` (1p) — BMC 9블록
- `gapflag-requirements.md` — MVP 요구사항 정의서 v0.1 (화면·스키마·산식·AC 12개, `docs/REQUIREMENTS`의 구버전)
- `tech-stack-guide.md` / 초기 `CLAUDE.md` — 초기 스택 검토 문서 ⚠️ **Streamlit 전제라 현재는 무효**
- `KU_AI_Nest_팀_아이디어_비교표.pdf` — 4인 아이디어 비교

---

## 7. 다음에 할 일 (우선순위 순)

### 즉시 (발표 D-2)

1. **팀 4명 전원 `uv sync` + `uvicorn` 실행 확인** — 아직 안 했다면 최우선. `build_cache.py`까지
   돌려서 `/matrix`에 점이 여러 개 찍히는지, 좌상단 사분면에도 점이 생겼는지 확인
2. **`data/seed_compounds.csv` 34건 팀 검수** (OI-01) — 여전히 미확정. O2까지 채워진 지금
   기회지수 분포가 어떻게 보이는지 `/matrix`로 먼저 본 뒤 사분면 균형 판단
3. S0(소개·산식 공개) 화면 — 아직 미착수. 발표에서 "왜 70점인가" 질문에 그 자리에서 답할
   유일한 수단이라 우선순위를 올릴 것

### 시간이 남으면

4. R4(EPO) — 승인 대기 중, 승인되면 `src_epo_service.py` 하나만 추가(산식은 이미 NULL을
   견디게 설계됨)
5. O3(Green Book 미승인) — §2-1에 적은 이유로 의도적 보류. 발표 이후 과제
6. `docs/REQUIREMENTS(요구사항정의서).md` R3/O2 반영 갱신 (발표엔 영향 없음, 문서 정합성용)

### 검증이 필요한 것

7. **동물약 개발 실무자 3~5명 인터뷰** — 이번 조사의 가장 큰 빈칸. 문제 크기와 지불 의사를 동시에 검증
8. Green Book 허가권자 파싱 → 미국 잠재 고객 수 실측 (MVP 코드 재사용)
9. 공공데이터포털 허가 현황 파싱 → 국내 업체 수 실측

---

## 8. 미결정 사항

| # | 항목 | 기한 | 상태 |
|---|---|---|---|
| OI-01 | 대상 성분 최종 목록 | 1회차 | ⚠️ AI 초안 34건, 팀 검수 필요 |
| OI-02 | 항체·단백질 의약품 우선 여부 확정 | 1회차 | 미결정 |
| OI-03 | 배포처 결정 및 빈 앱 배포 | 1~2회차 | Netlify 정적 목업 배포 경로는 있음(`netlify.toml`), 실 배포처 미확정 |
| OI-04 | 성분명 동의어 사전 초안 | 2회차 | 미착수 |
| OI-05 | §4-2 정규화 계수 실측 조정 | 3회차 | O2 반영 후 상단으로 퍼짐 확인, O3까지 채워지면 재판단 |
| OI-06 | 사분면 라벨 한글 최종 문구 | 3회차 | 미결정 |
| OI-07 | 전북 클러스터·한국동물약품협회 접촉 여부 | 미정 | 미결정 |

---

## 9. 다음 세션 시작 프롬프트 예시

```
Gap & Flag 프로젝트를 이어서 진행한다.
D:\Project\Ku_nest\GapFlag 폴더가 연결되어 있고,
docs/SESSION_HANDOFF_2.md 를 먼저 읽어라. git log와 origin 대비 로컬 상태도 확인해라
(핸드오프 문서가 실제 코드 상태보다 뒤처져 있을 수 있다).

오늘 할 일: [예) S0 소개·산식 공개 화면 착수]
```

**주의할 것**
- Streamlit·pandas·plotly·async 금지 판단은 **초기 대화의 오래된 결론이다.** 현재는 FastAPI 템플릿을 쓰므로 **async는 필수**이고, Streamlit은 쓰지 않는다.
- `uv.lock`에 있는 패키지만 쓴다. 새 의존성 추가 금지. `uv.lock`은 이은호만 수정 — `uv sync` 실행
  후 `git diff --stat uv.lock`으로 의도치 않은 변경이 없는지 매번 확인할 것
- `pandas`·`plotly`는 lock에 없다. 차트는 인라인 SVG.
- AI가 SQLAlchemy 1.x 문법(`session.query()`)이나 Pydantic v1(`@validator`)을 쓰지 않는지 확인할 것. 이 저장소는 **SQLAlchemy 2.0 + Pydantic v2**다.
- **이 핸드오프 문서 자체도 스냅샷이다.** 새 세션 시작 시 `git log`로 origin과 로컬을 대조하고,
  이 문서가 마지막으로 갱신된 날짜(맨 위) 이후 머지된 PR이 있는지 `gh pr list --state merged`로
  확인하는 습관을 들일 것.
- 프론트엔드는 없다 — `/matrix`, `/compound/{ingredient}` 등은 FastAPI가 Jinja2로 직접 그리는
  화면이다. `frontend/`(React) 폴더의 dev 서버 에러는 무시해도 된다.

---

## 10. 발표·심사 대비 메모

**가장 강한 한 장면** — Court(2013) 인용문을 띄우고 "업계는 이미 인체 데이터를 전용하는데, 문헌은 그게 부적합하다고 말한다"로 문제 정의를 끝낸다.

**반드시 나올 질문 세 개와 답**

1. *"왜 70점인가?"* → 총점만 보여주지 않는다. 구성요소·가중치·산식을 전부 공개하고 사용자가 슬라이더로 조정한다.
2. *"시장이 너무 좁지 않나?"* → 인정한다. SAM 추정 25억~35억 원. 그래서 고객을 "동물약 회사"가 아니라 **"인체 자산을 동물로 확장하려는 모든 바이오텍"**으로 정의했고, 장기 해자는 도구가 아니라 **축적되는 데이터**다.
3. *"경쟁사가 하면 되지 않나?"* → 대형 벤더는 인체 시장이 100배라 동물 쪽에 안 온다. 공공 도구는 인간 유전체 기반이라 종 축 추가가 확장이 아니라 재설계다.

**절대 하지 말 것** — 수치를 단정하기. AI 신약개발 시장은 리서치사별로 8배 차이가 난다. 항상 범위로 말한다.
