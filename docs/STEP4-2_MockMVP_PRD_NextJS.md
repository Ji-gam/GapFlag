# STEP 4-2 — Claude Code Mock MVP PRD (Next.js 실습용)

작성일 2026-08-29 · STEP 4-1의 Mini PRD를 Claude Code에서 바로 구현 가능한 Mock MVP PRD로 변환

> ⚠️ 참고: 이 문서는 실제 팀 저장소(FastAPI + Jinja2 + SQLite, `gap-and-flag`)와는 다른 스택(Next.js + TypeScript + Tailwind)을 전제로 한 별도의 3시간 실습용 Mock MVP PRD다. 팀 저장소의 기술 스택 결정(§1-2)을 대체하지 않는다.

---

# Claude Code Mock MVP PRD

## 1. 프로젝트 개요

- **프로젝트명**: Gap & Flag Mock MVP — 성분 위험×기회 스크리닝
- **서비스 목적**: 동물약 개발기업 R&D팀 연구원이 성분 단위로 위험(레드플래그)과 기회(연구 공백)를 한 화면에서 교차 확인하도록 해, "성분 단위 비교가 기존 수작업보다 유용한가"라는 하위가설을 검증한다.
- **핵심 사용자**: 동물약 개발기업 R&D팀에서 신약 후보 성분을 초기 스크리닝하는 연구원 1명(대표 페르소나)
- **핵심 사업가설**: 동물약 개발기업 R&D팀은 이 문제(위험·기회 데이터 분산)에 실제로 비용을 지불할 의사가 있다
- **이번 MVP에서 검증할 핵심가설**: 동물약 개발기업 R&D팀 연구원은 성분 단위로 위험×기회를 한 화면에서 비교하고 근거를 확인하면, 기존 방식(개별 DB 수작업 대조)보다 유용하다고 느끼고 다시 사용하고 싶어할 것이다

## 2. 개발 범위

### 이번 MVP에서 반드시 구현할 기능

1. 성분명 검색·조회
2. 2×2 위험×기회 매트릭스 표시
3. 성분 상세 + 근거 카드

### 구현하지 않을 기능

S3 후보 비교 화면, 실시간 외부 API 조회, EPO 특허(R4) 구성요소, Green Book 기반 R3·O3, 사용자 계정/로그인/회원가입, 데이터베이스, 관리자 기능, 성분 동의어 사전 자동화, 다국어 지원, 외부 AI API 연동

## 3. User Flow

입력(검색창에 성분명 입력 또는 대표 mock 성분 목록에서 선택 + 종 선택) → 처리(mock 데이터 파일에서 해당 성분·종의 R1~R4, O1~O3 원자료를 조회하고 지수 계산 함수를 실행 — **이 처리 단계 전체가 mock이며, 실제 openFDA·Open Targets·Europe PMC API는 호출하지 않는다**) → 결과(2×2 매트릭스 화면에서 사분면 위치 확인 → 상세 화면에서 구성요소별 근거 카드 확인)

## 4. 화면 구성

**화면명**: 성분 검색 화면
- 화면 목적: 사용자가 스크리닝할 성분과 종을 선택하게 함
- 주요 UI 요소: 검색 입력창, 종(개/고양이) 선택 토글, mock 성분 목록에서 바로 선택 가능한 리스트
- 사용자 행동: 성분명 입력 또는 목록 클릭 → 종 선택 → 조회 버튼 클릭
- mock 처리 여부: 검색 자체는 mock 데이터 파일 내 목록을 필터링하는 것으로 동작(외부 조회 없음)
- 다음 화면 또는 결과: 2×2 매트릭스 화면으로 이동

**화면명**: 2×2 매트릭스 화면 (S1)
- 화면 목적: 선택한 성분의 위험×기회 사분면 위치를 인라인 SVG로 보여줌
- 주요 UI 요소: 2×2 매트릭스(위험지수 X축, 기회지수 Y축), 사분면 라벨("비어 있는 이유가 있음" 등), 선택 성분의 위치 마커, 위험지수·기회지수·커버리지 % 표시
- 사용자 행동: 마커 클릭 시 상세 화면으로 이동
- mock 처리 여부: mock 데이터로 미리 계산된 지수값을 그대로 렌더링
- 다음 화면 또는 결과: 성분 상세·근거 카드 화면

**화면명**: 성분 상세·근거 카드 화면 (S2)
- 화면 목적: 위험·기회 각 구성요소(R1~R4, O1~O3)별 근거를 카드 형태로 보여줌
- 주요 UI 요소: 구성요소별 카드(값, 출처명, 요약, 원문 링크), 값이 없는 구성요소는 회색 처리 + "위험이 없다는 뜻이 아닙니다" 문구, 하단 면책 문구
- 사용자 행동: 카드 확인, 원문 링크 클릭(mock에서는 실제 이동하는 예시 URL), 뒤로가기
- mock 처리 여부: 전체 mock 데이터 기반
- 다음 화면 또는 결과: 없음(종료 화면) 또는 검색 화면으로 복귀

## 5. 핵심 기능

**기능명**: 성분 검색·조회
- 입력값: 성분명(문자열), 종(dog | cat)
- 처리 방식: mock 성분 목록 배열을 성분명으로 필터링
- 출력값: 일치하는 성분 목록 또는 선택된 성분 1건
- 더미 데이터 또는 mock 처리 방식: `data/mockCompounds.ts`에 정의된 고정 배열 사용
- 향후 실제 기능/API 연결 시 교체할 영역: 성분명 정규화(동의어 사전) 및 DB 조회 로직으로 교체

**기능명**: 위험·기회 지수 계산
- 입력값: 선택된 성분의 구성요소 원자료(R1~R4, O1~O3 각각 값 또는 null)
- 처리 방식: 확정된 산식(각 구성요소를 0~100으로 환산 후 가중합, NULL은 분자·분모에서 제외)에 따라 위험지수·기회지수·커버리지 %를 계산하는 순수 함수
- 출력값: `{ riskIndex, opportunityIndex, coverage }`
- 더미 데이터 또는 mock 처리 방식: 계산 로직 자체는 실제 산식 그대로 구현하되, 입력 원자료가 mock임
- 향후 실제 기능/API 연결 시 교체할 영역: 없음(이 계산 함수는 실제 데이터가 들어와도 그대로 재사용 가능하도록 `lib/scoreCalculator.ts`에 순수 함수로 분리)

**기능명**: 근거 카드 표시
- 입력값: 성분의 구성요소별 원자료(값, 출처, 요약, URL)
- 처리 방식: 구성요소 배열을 순회하며 카드 렌더링, 값이 null이면 회색 스타일 적용
- 출력값: 카드 UI 목록
- 더미 데이터 또는 mock 처리 방식: mock 데이터의 출처·요약·URL 필드를 그대로 사용
- 향후 실제 기능/API 연결 시 교체할 영역: `data/mockCompounds.ts`를 실제 API 조회 결과로 교체(컴포넌트는 동일 인터페이스 유지)

## 6. 데이터 구조

**1. 사용자가 실제로 입력하는 데이터**

```typescript
interface UserQuery {
  ingredientName: string; // 예: "carprofen"
  species: "dog" | "cat"; // 예: "dog"
}
```

**2. Mock MVP 내부에서 사용하는 예시 데이터**

```typescript
interface ScoreComponent {
  value: number | null; // null = 데이터 없음(확인 못함), 0과 다름
  sourceName: string; // 예: "openFDA ADAE"
  summary: string; // 예: "최근 3년간 이상반응 보고 12건"
  sourceUrl: string; // 예: "https://open.fda.gov/apis/animalandveterinary/event/"
}

interface CompoundMock {
  ingredientName: string;
  species: "dog" | "cat";
  risk: {
    r1: ScoreComponent; // 임상 중단 이력
    r2: ScoreComponent; // 동물 이상반응
    r3: ScoreComponent; // 승인·철회 이력
    r4: ScoreComponent; // 특허 밀집도
  };
  opportunity: {
    o1: ScoreComponent; // 문헌 희소성
    o2: ScoreComponent; // 임상 부재
    o3: ScoreComponent; // 미승인 여부
  };
}
```

예시값(carprofen / dog):
```
r1: { value: null, sourceName: "Open Targets", summary: "사람 임상 중단 이력 확인 안 됨", sourceUrl: "https://platform.opentargets.org/" }
r2: { value: 45, sourceName: "openFDA ADAE", summary: "최근 보고 이상반응 다수", sourceUrl: "https://open.fda.gov/apis/animalandveterinary/event/" }
r3: { value: 20, sourceName: "FDA Green Book", summary: "승인 유지 중", sourceUrl: "#" }
r4: { value: null, sourceName: "EPO OPS", summary: "특허 데이터 미확인", sourceUrl: "#" }
o1: { value: 60, sourceName: "Europe PMC", summary: "관련 문헌 다소 적음", sourceUrl: "https://europepmc.org/" }
o2: { value: null, sourceName: "ClinicalTrials.gov", summary: "임상시험 등록 정보 미확인", sourceUrl: "#" }
o3: { value: 0, sourceName: "FDA Green Book", summary: "이미 승인됨", sourceUrl: "#" }
```

## 7. 대표 Mock 시나리오

- **사용자 상황**: R&D 연구원이 "carprofen"이라는 성분을 개(dog)에게 적용하는 신약 후보로 검토 중이며, 위험한지와 아직 공백이 있는지를 확인하고 싶다
- **사용자 입력**: 성분명 "carprofen", 종 "dog"
- **mock 처리**: `data/mockCompounds.ts`에서 carprofen/dog 조합을 조회(실제 API 호출 없음, 이 지점이 mock 처리 지점)
- **처리 결과**: R1=null, R2=45, R3=20, R4=null → 확인된 값만으로 위험지수 계산, 커버리지 50%. O1=60, O2=null, O3=0 → 기회지수 계산, 커버리지 66%
- **최종 출력 결과**: 매트릭스 화면에 "우선 검토" 사분면 근처 위치로 마커 표시, 상세 화면에 4개 위험 카드(2개는 회색 NULL 표시)와 3개 기회 카드(1개는 회색 NULL 표시), 하단에 "데이터 없음은 위험이 없다는 뜻이 아닙니다" 및 "본 도구는 참고용이며 의료·규제 판단을 대신하지 않습니다" 문구
- **이 시나리오를 통해 확인할 핵심가설**: 사용자가 이 화면만 보고 "위험 일부는 확인됐지만 기회도 있다"는 판단을 스스로 내릴 수 있는가

이 mock 데이터와 결과는 테스트용 예시이며, 실제 의료·규제 판단이나 실제 API 조회 결과가 아니다.

## 8. 프로젝트 구조

```
app/
  page.tsx                    # 성분 검색 화면
  matrix/page.tsx             # 2×2 매트릭스 화면
  compound/[name]/page.tsx    # 성분 상세·근거 카드 화면
components/
  SearchForm.tsx
  MatrixChart.tsx
  EvidenceCard.tsx
data/
  mockCompounds.ts
lib/
  scoreCalculator.ts
types/
  compound.ts
```

원칙: 필요하지 않은 폴더 미리 생성 금지, 불필요한 추상화·과도한 컴포넌트 분리 금지, 이번 MVP에서 사용하지 않는 파일 생성 금지, 향후 실제 분석 API로 교체할 mock 분석 로직(`lib/scoreCalculator.ts`, `data/mockCompounds.ts`)만 별도 분리.

## 9. 디자인 가이드

기존 Mini PRD에서 정해진 디자인 요구사항은 없으므로, 새로운 브랜드 컨셉이나 복잡한 디자인 시스템 없이 깔끔하고 읽기 쉬운 기본 웹 UI 수준으로 구성한다.

우선순위: 1. 핵심 결과(사분면 위치·근거 카드)의 가독성 2. 검색→매트릭스→상세 흐름 이해 3. 모바일 대응 4. 시각적 완성도

## 10. Claude Code 구현 지시사항

1. 현재 폴더와 Next.js 프로젝트 구조 확인
2. `app/page.tsx`, `app/matrix/page.tsx`, `app/compound/[name]/page.tsx` 생성
3. `SearchForm`, `MatrixChart`, `EvidenceCard` 공통 컴포넌트 생성
4. `data/mockCompounds.ts`에 carprofen/dog 대표 mock 데이터 생성
5. 성분명·종 입력 기능 구현 (SearchForm)
6. `lib/scoreCalculator.ts`에 위험·기회 지수 계산 순수 함수 구현 (mock 원자료 입력)
7. 입력 → 계산 → 결과 화면으로 이어지는 사용자 흐름 연결 (page 간 라우팅)
8. 매트릭스 화면(인라인 SVG)과 상세·근거 카드 화면 구현
9. Tailwind CSS로 기본 반응형 UI 적용
10. 빈 입력·존재하지 않는 성분명에 대한 최소한의 에러 메시지 처리
11. 로컬 실행(`npm run dev`) 및 빌드 오류 확인
12. Vercel에 배포 가능한 상태로 정리

중요: 오류 처리는 MVP 실행에 필요한 최소 수준만 구현하고, 테스트 코드·관리자 기능·DB·인증 등 Mini PRD에 없는 개발범위는 추가하지 않는다.

## 11. MVP 완료 조건

- 사용자가 검색 화면에서 시작해 매트릭스 화면과 상세·근거 카드 화면까지 도달할 수 있음
- carprofen/dog 대표 mock 시나리오가 정상 동작함
- Mini PRD에서 정의한 핵심 결과(사분면 위치, 지수 값, 커버리지 %, 근거 카드, NULL 회색 표시, 면책 문구)가 화면에 모두 표시됨
- "성분 단위 위험×기회 비교가 유용한가"라는 핵심가설을 사용자에게 실제로 테스트할 수 있는 상태임
- 외부 API, API Key, DB 없이 로컬에서 실행 가능함
- build 오류 없이 Vercel 배포가 가능한 상태임

---

# Claude Code 시작 명령

아래 PRD를 기준으로 추가 질문 없이 바로 파일 생성과 구현을 시작해줘.

개발환경: Next.js, TypeScript, React, Tailwind CSS. 프론트엔드와 필요한 간단한 서버 기능은 하나의 Next.js 프로젝트 안에서 구성하고, 별도 Express 서버나 데이터베이스는 사용하지 않는다. 데이터가 필요한 경우 로컬 상수·JSON·mock 데이터 파일을 사용하고, 환경변수나 외부 서비스 설정 없이 로컬 실행이 가능하도록 구성한다. 외부 AI API, API Key, 별도 인증·백엔드 인프라·클라우드 스토리지는 추가하지 않는다.

기술 스택을 다시 묻지 말 것. API 사용 여부를 다시 묻지 말 것. 데이터베이스 사용 여부를 다시 묻지 말 것. 구현 방법을 사용자에게 선택하게 하지 말 것. 임의의 기능을 추가하지 말 것. 아래 Mini PRD에 없는 사용자 입력을 추가하지 말 것. mock 데이터를 실제 분석 결과처럼 표현하지 말 것. 위 PRD 범위 안에서 바로 파일 생성과 구현을 시작할 것. 구현 후 로컬 실행 및 build 오류까지 확인할 것.

---

[Mini PRD 전체]

# Mini PRD

## 1. 프로젝트명

Gap & Flag MVP — 성분 위험×기회 스크리닝

## 2. 서비스 목적

동물약 개발기업 R&D팀 연구원이 성분 단위로 위험(레드플래그)과 기회(연구 공백)를 한 화면에서 교차 확인하도록 해, "성분 단위 비교가 기존 수작업보다 유용한가"라는 하위가설을 검증한다.

## 3. 핵심 사용자

동물약 개발기업 R&D팀에서 신약 후보 성분을 초기 스크리닝하는 연구원 1명(대표 페르소나)

## 4. 핵심 사업가설

동물약 개발기업 R&D팀은 이 문제(위험·기회 데이터 분산)에 실제로 비용을 지불할 의사가 있다.

## 5. 이번 MVP에서 검증할 가설

동물약 개발기업 R&D팀 연구원은 성분 단위로 위험×기회를 한 화면에서 비교하고 근거를 확인하면, 기존 방식(개별 DB 수작업 대조)보다 유용하다고 느끼고 다시 사용하고 싶어할 것이다.

## 6. User Flow

입력(성분명·종 선택) → 처리(DB 조회 + 지수 계산) → 결과(2×2 매트릭스 위치 + 근거 카드)

## 7. 핵심 기능

1. 성분명 검색·조회 — 사전 등록된 성분 목록에서 검색하거나 직접 입력
2. 2×2 위험×기회 매트릭스 표시 (인라인 SVG)
3. 성분 상세 + 근거 카드 (구성요소별 출처 링크, NULL 항목 회색 표시)

## 8. 사용할 데이터

- 사용자 입력 데이터: 성분명, 종(개/고양이)
- 서비스가 처리할 데이터: openFDA ADAE(R2), Open Targets(R1), Europe PMC(O1) 배치 수집 결과, 원본 API 응답(raw JSON) 포함
- 아직 확보되지 않았거나 검증이 필요한 데이터: [추가 검증 필요] EPO 특허(R4), Green Book(R3·O3) — API 키 발급·파싱 미완료 / [추가 검증 필요] 대상 성분 30~50건 최종 목록 확정 여부

## 9. 주요 화면

1. 성분 검색 화면
2. 2×2 매트릭스 화면 (S1)
3. 성분 상세·근거 카드 화면 (S2)

## 10. 결과 화면에 반드시 표시할 정보

사분면 위치, 위험지수·기회지수 값, 구성요소별 커버리지 %, 근거 카드(출처 링크 포함), NULL 항목 회색 표시 + "위험이 없다는 뜻이 아닙니다" 문구, 하단 면책 문구("참고용이며 의료·규제 판단을 대신하지 않습니다")

## 11. MVP 성공 기준

- 핵심가치 이해: 사용자가 매트릭스를 보고 별도 설명 없이 "위험은 낮은데 아직 공백이 크다" 같은 해석을 스스로 말할 수 있는가
- 문제 해결 정도: 기존에 여러 DB를 수작업으로 대조하던 것과 비교해 "더 빠르다/명확하다"고 느끼는가
- 재사용 의향: 다른 성분으로도 다시 써보고 싶다고 말하는가
- 지불의향: 이 도구에 팀 예산으로 비용을 지불할 의향이 있는지 물어보고 반응을 기록
- 구체적 수치 기준은 [추가 검증 필요] — 실제 사용자 테스트에서 관찰해 채울 항목

## 12. 이번 MVP에서 구현하지 않을 기능

S3 후보 비교, 실시간 API 조회, EPO 특허(R4) 구성요소, Green Book 기반 R3·O3, 사용자 계정/로그인, 성분 동의어 사전 자동화, 다국어 지원
