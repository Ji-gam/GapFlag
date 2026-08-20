# AGENTS.md — 프로젝트 단일 진입점

v4.0 · 이력: `git log AGENTS.md`. 모든 에이전트 매 세션 필독. `CLAUDE.md`/`.antigravity/rules/AGENTS.md`=리다이렉트. 불확실하면 추측 금지, 확인. 이 문서는 정책+라우팅만 — 각 항목의 상세 규칙은 아래 대상 문서에만 존재(중복 서술 금지).

> 이 레포는 도메인 로직을 뺀 뼈대(스켈레톤) 템플릿이다. 레이어 우선 구조(Router→Service→
> Repository)의 FastAPI 백엔드 + Vite/React 프론트엔드 + 재사용 가능한 `auth_kit`/
> `security_kit` 인증·보안 모듈로 구성된다. 실제 서비스의 도메인 모델/라우터/화면은
> 프로젝트마다 각 레이어 폴더에 새로 추가한다.

0. 절대원칙
- 확인질문 최소화 — 부족분은 가정 후 완료보고에 Assumptions로 기록. 모호하면 임의진행 대신 가정을 먼저 설명. 사용자가 피하라고 한 접근은 같은 대화 내 재시도 안 함
- 중단은 §6표 "반드시멈춤" 항목일 때만. 그 외(변수명/함수분리/에러문구)는 자체결정. `STOP` 입력시 즉시중단(§4)
- 공유구역(여러 도메인이 함께 쓰는 코드) 수정 필요시 이유를 완료보고에 명시

1. 디렉토리=소유권 (전체 구조/파일역할: `docs/CODING_RULES.md` §2/§3)

```
app/            apis/v1/ dtos/ services/ repositories/ models/ tests/
                dependencies/ core/ [공유]
ai_worker/      RAG/LLM 백그라운드 워커(도메인 무관 게이트웨이) | core/[공유]
frontend/src/   pages/ hooks/ [화면소유]
                api/ components/ routes/ store/ types/ [공유]
envs/ infra/ scripts/ [공유]
docs/           규칙/기여/트러블슈팅 문서
```
새 도메인을 추가할 때는 폴더가 아닌 파일명 접두어로 소유권을 구분한다(예: `acc_service.py`,
`acc_routers.py`). 도메인 코드 체계(예: `ACC`, `MAT` 등)는 프로젝트별 요구사항 문서에서
정의하고 한 번 정하면 새로 만들지 않는다.

2. 스택
백엔드 FastAPI, DB MySQL, 프론트 React(+Vite), 인프라는 프로젝트별 제약사항에 따름. 상세는
`pyproject.toml`/`frontend/package.json`. 코드 컨벤션은 `docs/CODING_RULES.md`.

3. 데이터 모델 확장
전체 규칙: `docs/CODING_RULES.md` §2-1. 이 템플릿은 도메인 모델을 포함하지 않는다 —
`app/models/base.py`(DeclarativeBase)만 있는 상태에서 시작해, 서비스에 맞는 모델을
새로 설계한다. 민감정보(개인정보 등)를 다루는 컬럼은 컬럼단위 암호화를 검토한다
(`security_kit`의 `EncryptedStr` 참고).

4. Drill-Me/STOP
트리거(하나라도): 새 화면/컴포넌트/플로우 요청, 텍스트 화면스펙(진입점/컴포넌트/로딩·빈·에러상태/인터랙션→API) 없음, 기존 스펙 범위 초과.
생략: 스펙 안에서만 구현, 순수 버그수정/내부 리팩토링.
질문세트(답 없는 것만 콕 집어 되물음, 코드 먼저 안 씀): 진입점(탭/화면) / 구성 컴포넌트+필수·선택 / 로딩·빈·에러 상태 표시 / 인터랙션→API 매핑.
판단기준: "이 요구사항만으로 두 사람이 다른 화면을 만들 수 있는가"→그렇다면 미완료. 답 다 있으면 "이렇게 이해했다" 요약확인만. 끝나면 짧은 텍스트스펙 동의받고 코드 작성.
STOP: 메시지 어디든 `STOP`→ 작성중이면 즉시멈춤 / 이해내용 요약 / 미답 문항만 재확인 / 답 받기 전 재산출 안 함. 취소 아님, 재확인모드 전환.

5. 브랜치/커밋/PR/구현순서/로컬실행/검증
전부 `docs/CONTRIBUTING.md`. 에이전트는 PR 생성+CI확인까지가 범위, 직접 머지 안 함. 에러 발생시 `docs/TROUBLESHOOTING.md`.

6. 결정됨/반드시멈춤
결정됨(재확인불필요, 프로젝트가 정한 정책은 여기 대신 요구사항 문서에 정리): 비밀번호는 단방향 해시 저장 · JWT 세션 · 무상태 API설계 · `.env`/API키/시크릿 코드·커밋·PR에 하드코딩 금지.
반드시멈춤: 공유구역/DB공통스키마 직접수정 필요 · 사전 승인 없는 외부API/서비스연동 · 개인정보/보안 비가역작업(암호화방식, 민감정보 로직, 영구삭제) · 두 요구사항이 모순 · DB스키마/ORM/인증방식 등 되돌리기 힘든 결정 · 요청이 모호하거나 여러 도메인에 걸침 · 이미 정해진 것 다르게 재해석해야 할듯.
표 밖은 위 원칙+합리적 가정으로 진행.

7. 범위경계
- 요청과 무관한 파일 수정 금지
- `.env`/API키/시크릿 코드·커밋·PR에 하드코딩 금지 — `envs/example.*.env`엔 키 이름만
- 실코드가 `CODING_RULES.md`와 다르면 팀합의 없는 개인작업 가능성 — 그대로 안 따르고 재작업 필요여부 확인

8. 완료 자가검증
확인: 테스트포함 / `ruff`·`pytest`·`tsc`·`lint` 통과 / 변경범위가 요청 범위로 한정(`git diff --stat`) / 새 엔드포인트 summary·description·responses·Field(description=...) / DB변경시 Alembic 마이그레이션 동반 / 커밋·브랜치명 규칙 준수(CONTRIBUTING§3,§8). 검증커맨드: `docs/CONTRIBUTING.md` §7.

9. 문서지도
`docs/CONTRIBUTING.md`(구조/브랜치/이슈·PR/TDD순서/로컬실행/검증) · `docs/CODING_RULES.md`(계층/폴더/네이밍/API·DB포맷/프론트규칙/TDD품질기준/ERD/Swagger) · `docs/TROUBLESHOOTING.md`(로컬실행 에러) · `docs/FRONTEND_UI_GUIDE.md`(디자인시스템/Tailwind+shadcn) · `auth_kit/README.md`(회원가입/인증 드롭인 모듈) · `security_kit/README.md`(도메인 무관 보안 모듈)
