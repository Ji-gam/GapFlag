# SESSION_HANDOFF.md — 다음 세션 인수인계

v1.4 · 작성 2026-08-16, 갱신 2026-09-01 → 2026-09-04(v1.2 → v1.3 → v1.4) · 이 문서 하나만 읽으면 이전 대화 없이 이어서 작업할 수 있다.

**v1.4에서 바뀐 것**: v1.3 이후 [PR #23](https://github.com/Ji-gam/GapFlag/pull/23)(gitignore 정리)과
[PR #24](https://github.com/Ji-gam/GapFlag/pull/24)(SESSION_HANDOFF v1.3 문서)가 머지됐고,
이어서 **O3(미승인 여부) 수집 서비스가 [PR #25](https://github.com/Ji-gam/GapFlag/pull/25)로 머지**됐다 —
v1.3에서 "의도적 보류"였던 항목이 닫히며 **기회 지수 커버리지가 66.7% → 100%**로 올랐다.
이제 R4(EPO 특허)만 미수집이고, 잘라내는 순서(§4-6)에 남은 건 S3 화면과 R4 둘뿐이다.
§0·§2-1·§2-3·§3-2·§4-2·§4-6·§6·§7을 갱신했다. §1·§3-1·§3-3~3-5·§4-1·§4-3~4-5·§5·§8·§10은 그대로 유효.

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
| 현재 단계 | **화면 4개 전부 동작함** (검색·매트릭스·상세·소개). 수집 서비스 **6종(R1/R2/R3/O1/O2/O3)** 실동작. **기회지수 커버리지 100%**, 위험지수 커버리지 75%(R4만 미수집). S3(비교)는 여전히 미착수(P1, 잘라도 됨), 시드 성분 34건은 초안(팀 검수 전) |

---

## 1. 확정된 결정

(v1.3과 동일 — 아이디어 선정 경위·팀명·핵심 컨셉·1차 키·DB/화면 스택 확정 사항. `docs/SESSION_HANDOFF_3.md` §1 참고)

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
app/services/src_greenbook_service.py     R3 자발적 승인철회 + O3 미승인 여부 (FDA Green Book)   ✅ NEW(O3)
app/services/src_europepmc_service.py     O1 문헌 희소성 (Europe PMC)                            ✅
app/services/src_clinicaltrials_service.py O2 사람 임상시험 부재 (ClinicalTrials.gov v2)         ✅
app/core/utils/scr_normalize.py    구성요소별 0~100 환산 함수 (순수 함수, o3_unapproved 포함)     ✅ NEW(O3)
app/services/scr_score.py          위험·기회 지수 계산 (NULL 제외, 커버리지 계산)                 ✅
app/apis/cmp_pages.py              GET / , GET /matrix , GET /compound/{ingredient} , GET /about ✅
app/templates/                     base.html, search.html, matrix.html, detail.html, about.html  ✅
scripts/build_cache.py             CSV 읽어 6종 API 순차 수집 → DB 저장 (수동 실행)              ✅ NEW(O3 배선)
data/seed_compounds.csv            대상 성분 34건 — **초안, 팀 검수 전** (OI-01 미확정)          ⚠️
```

**아직 없는 것**: R4(EPO OPS 특허) 수집 서비스뿐. 산식이 NULL을 견디도록 설계돼 있어 화면은
정상 동작하고, 위험지수 커버리지는 75%(R1~R3만 반영)로 나온다.

**O3 구현 방식과 알려진 한계** (v1.3까지의 "의도적 보류" 사유가 이번에 이렇게 해소됨):
FDA Green Book 사이트를 직접 열어 확인한 결과, R3가 쓰는 Section 6(자발적 철회) 외에
**Section 2(Active Ingredients) export**가 별도로 존재하고, 여기 실린 성분명 집합에
포함돼 있으면 "승인됨"으로 판정할 수 있다. 다만 **이 export에는 종(dog/cat) 컬럼이
아예 없다**(`Application Number, Active Ingredients, Trade Name, Ingredient` 4컬럼뿐,
2334행 실측 확인). 즉 애초에 "개는 승인, 고양이는 미승인" 같은 종별 구분은 이 소스만으로는
불가능 — **성분 단위(species 무관)로만 판정**하고, 그 사실을 `/about` 화면에 명시했다.
R3(승인철회 이진화)와 같은 급의 단순화이며, ponytail 주석으로 남겨둠
([scr_normalize.py](app/core/utils/scr_normalize.py) `o3_unapproved`).

### 2-2. S0(소개·산식 공개) 화면

v1.3과 동일 — `GET /about` 정적 렌더링, 산식 전문·데이터 출처·NULL≠0 원칙 공개.
**O3 행이 "❌ 의도적 보류"에서 "✅ 성분 단위 판정(종 구분 불가, 알려진 한계)"로 갱신됨.**

### 2-3. 재수집 결과 (2026-09-04, `data/gapflag.db` 실측, O3 반영 기준)

- 35행(성분×종 조합) 전부 **기회지수 커버리지 100%**(O1+O2+O3 전부 채워짐, v1.3의 66.7%에서 상승)
- 위험지수 커버리지는 75%(R1~R3, R4만 없음)로 v1.3과 동일
- O3 값 실측 예: carprofen·meloxicam(기존 승인 동물약) → 0점 / gabapentin·masitinib(인체약 전용,
  동물용 미승인) → 100점 — 산식 의미대로 갈림을 확인함
- `uv run python -m scripts.build_cache` 실행 결과 35/35 성공, 실패 0

### 2-4. `/matrix` 화면

v1.3과 동일한 전체 산점도 구조. O3 반영 후 브라우저로 직접 확인한 결과, 좌상단
"비어 있는 이유가 있음" 사분면에 점이 이미 찍혀 있고, 지수 NULL(회색) 항목이 매트릭스
아래에서 사라짐(기회지수 커버리지 100%와 일치).

### 2-5. Alembic / 테스트

- Alembic 리비전 1개, 스키마 동결 중 (v1.3과 동일, O3는 새 컬럼 없이 기존 `component_key`
  값만 늘어난 것이라 마이그레이션 불필요)
- `app/tests/` 테스트 **45개**(v1.3의 37 + O3 관련 8: greenbook 6, normalize 2), 전부 통과

### 2-6. 팀원 셋업 (설치 3개)

v1.3과 동일. `build_cache.py`가 이제 6종 API를 호출하므로 수집 시간이 약간 늘 수 있음.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv python install 3.13
uv sync --group app --group dev      # ai 그룹은 절대 넣지 않는다
Copy-Item envs\example.local.env .env
uv run alembic upgrade head
uv run python -m scripts.build_cache  # 34개 성분 수집 (몇 분 걸림)
uv run uvicorn app.main:app --reload
```

---

## 3. 시장조사 핵심 수치 (재조사 불필요)

v1.3과 대부분 동일. `docs/SESSION_HANDOFF_3.md` §3 참고. 변경된 것만 아래.

### 3-2. 데이터 소스 갱신

| 소스 | 용도 | 조건 | 수집 상태 |
|---|---|---|---|
| **FDA Green Book** | 위험 R3 승인·철회 / 기회 O3 미승인 | 무료. **공식 API 없음 — 파일 파싱 필요** | ✅ R3·O3 **둘 다 구현됨**(v1.3까지 O3 보류였음) |

나머지 행(openFDA, Open Targets, EPO OPS, Europe PMC, ClinicalTrials.gov)은 v1.3과 동일.

---

## 4. 제품 설계

### 4-2. 지수 산식 갱신

| ID | 구성요소 | 환산식 | 수집 상태 |
|---|---|---|---|
| O3 | 미승인 | 미승인 100 · 승인 0 (성분 단위, 종 구분 불가 — §2-1 한계) | ✅ |

나머지 R1~R4·O1·O2는 v1.3과 동일. O3 반영 후 실측(35건, 2026-09-04): 기회지수 커버리지
100%. 분포 재확인은 `/matrix`에서 가능 — §4-6·§7 참고.

(그 외 §4-1 조인 키, §4-3 타협 불가 원칙, §4-4 파일 배치, §4-5 화면 3개+소개는 v1.3과 동일)

### 4-6. 잘라내는 순서 (갱신)

~~① S3 비교 → ② 실시간 조회 → ③ 특허(EPO) 구성요소 → ④ O3~~
→ **O3가 구현 완료되어 목록에서 빠짐.** 남은 건 두 개뿐:

① S3 비교 화면 → ② 특허(EPO, R4) 구성요소

**절대 버리지 않는 것**: 2×2 매트릭스 / 근거 카드와 원문 링크 / "데이터 없음" 회색 표시 —
전부 지금 화면에 살아있다.

---

## 5. 역할 분담

v1.3과 동일. `docs/SESSION_HANDOFF_3.md` §5 참고.

---

## 6. 지금까지 만든 산출물

저장소 안 (v1.3 목록에 추가):
- `docs/SESSION_HANDOFF.md`(v1.0) → `_1`(v1.1) → `_2`(v1.2) → `_3`(v1.3) → **`_4`(이 문서, v1.4)**
  — 과거 버전도 지우지 말고 그대로 둔다(이력 추적용)

그 외 v1.3과 동일 (`docs/MVP_SCOPE.md`, `docs/REQUIREMENTS`, `docs/BEGINNER_GUIDE.md`,
`data/seed_compounds.csv`, 저장소 밖 PDF·시장조사 자료).

---

## 7. 다음에 할 일 (우선순위 순)

### 즉시 (발표 D-2 ~ D-1)

1. **팀 4명 전원 `uv sync` + `uvicorn` 실행 확인** — `build_cache.py`까지 돌려서 `/matrix`에
   점이 여러 개 찍히는지, 좌상단 사분면 점 개수가 늘었는지(O3 반영 후) 확인
2. **`data/seed_compounds.csv` 34건 팀 검수** (OI-01, 여전히 미확정) — 기회지수 커버리지가
   100%가 된 지금 사분면 분포가 어떻게 보이는지 `/matrix`로 먼저 본 뒤 판단
3. `docs/REQUIREMENTS(요구사항정의서).md`에 O3 반영 갱신 (발표 영향 없음, 문서 정합성용)

### 시간이 남으면

4. R4(EPO 특허) — 키 승인 대기 중. 승인되면 `src_epo_service.py` 하나만 추가(산식은 이미
   NULL을 견디게 설계됨). **이제 유일하게 남은 미수집 구성요소.**
5. S3(후보 비교) 화면 — P1, 시간이 남을 때만. **이제 유일하게 남은 미착수 화면.**

### 검증이 필요한 것

6. **동물약 개발 실무자 3~5명 인터뷰** — 이번 조사의 가장 큰 빈칸
7. Green Book 허가권자 파싱 → 미국 잠재 고객 수 실측 (O3에서 이미 Section2 파싱 코드가
   생겼으니 재사용 가능)
8. 공공데이터포털 허가 현황 파싱 → 국내 업체 수 실측

---

## 8. 미결정 사항

v1.3과 동일. `docs/SESSION_HANDOFF_3.md` §8 참고. OI-05(정규화 계수 재조정)는 O3까지
반영된 지금 재판단 시점이 됐다 — §7의 2번과 함께 처리.

---

## 9. 다음 세션 시작 프롬프트 예시

```
Gap & Flag 프로젝트를 이어서 진행한다.
D:\Project\Ku_nest\GapFlag 폴더가 연결되어 있고,
docs/SESSION_HANDOFF_4.md 를 먼저 읽어라. git log와 origin 대비 로컬 상태도 확인해라
(핸드오프 문서가 실제 코드 상태보다 뒤처져 있을 수 있다).

오늘 할 일: [예) data/seed_compounds.csv 34건 팀 검수]
```

**주의할 것** (v1.3과 동일, 그대로 유효)
- `uv.lock`에 있는 패키지만 쓴다. 새 의존성 추가 금지. `uv.lock`은 이은호만 수정
- `pandas`·`plotly`는 lock에 없다. 차트는 인라인 SVG
- SQLAlchemy 2.0 + Pydantic v2 문법만 사용 (`session.query()`, `@validator` 금지)
- **이 핸드오프 문서 자체도 스냅샷이다.** `git log`로 origin과 로컬을 대조하고, 마지막 갱신일
  이후 머지된 PR이 있는지 `gh pr list --state merged`로 확인하는 습관을 들일 것
- 프론트엔드는 없다 — 전부 FastAPI가 Jinja2로 직접 그리는 화면

---

## 10. 발표·심사 대비 메모

v1.3과 동일. `docs/SESSION_HANDOFF_3.md` §10 참고 — Court(2013) 인용, 예상 질문 3개와 답,
"수치를 단정하지 말 것" 원칙 그대로 유효. 추가로 O3까지 채워져 기회지수 커버리지가 100%가
됐으므로 "이 점수는 얼마나 신뢰할 수 있나?" 질문에 "위험 75% · 기회 100% 커버리지, 부족한
부분은 회색으로 숨기지 않고 그대로 보여준다"고 답할 수 있다.
