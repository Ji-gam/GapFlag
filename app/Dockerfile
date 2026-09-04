FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. uv 설치 (공식 이미지에서 복사해오는 가장 깔끔한 방법)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 2. 의존성 패키지 관리 파일을 컨테이너 내부에 복사합니다.
COPY pyproject.toml uv.lock alembic.ini ./

# 3. pyproject.toml에 명시된 의존성 패키지 중에서 'app' 그룹만 설치합니다.
RUN uv sync --group app --no-dev --frozen

# 4. 로컬 소스 코드를 컨테이너 내부로 복사합니다. (alembic.ini의 script_location이 가리키는 app/core/db/migrations 포함)
# app/main.py와 app/models/__init__.py가 auth_kit·security_kit을 최상위 패키지로 import하므로
# 이 두 디렉터리도 같이 복사해야 한다 — 빠지면 컨테이너 기동/마이그레이션이
# ModuleNotFoundError로 죽는다(venv 실행은 저장소 루트가 cwd라 안 겪던 문제).
COPY ./app ./app
COPY ./auth_kit ./auth_kit
COPY ./security_kit ./security_kit
# data/gapflag.db는 .gitignore 대상이라 여기 안 들어온다(의도된 동작) — seed_compounds.csv만
# 딸려온다. scripts/는 build_cache.py(무료 호스팅 슬립 후 재기동 시 자동 재수집용).
COPY ./data ./data
COPY ./scripts ./scripts

# 5. 해당 이미지를 활용하여 도커컨테이너 실행시 실행되는 명령어입니다.
# FastAPI를 uvicorn을 활용하여 비동기 환경으로 서버를 실행합니다.
# --no-sync 옵션은 uv run시 uv.lock파일과 환경에 설치된 패키지들을 비교하여 없는 패키지를 설치하기 때문에
# 불필요한 의존성을 설치하지 않기 위해 사용합니다.
# docker-compose는 command:로 이 CMD를 덮어쓰므로(마이그레이션+--reload) 로컬 개발엔 영향 없다.
# 여기서만 마이그레이션+데이터 수집을 같이 실행하는 이유: Render 무료 티어처럼 디스크가
# 영구 보존 안 되는 호스팅에선(슬립 후 재기동마다 컨테이너가 새로 뜸) 이 CMD가 재기동될
# 때마다 build_cache.py로 성분 데이터를 다시 채워야 화면에 값이 남는다. 실패해도 서버는
# 뜬다(build_cache.py가 성분별로 실패를 삼키고 계속 진행 — 화면은 그 성분만 NULL로 표시).
# PORT는 Render/Railway가 주입하는 환경변수이고, 없으면(로컬 docker run 등) 8000이 기본값이다.
CMD ["sh", "-c", "uv run --no-sync alembic upgrade head && uv run --no-sync python -m scripts.build_cache; uv run --no-sync uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
