from fastapi import APIRouter

# from auth_kit.router import auth_router

# 각 도메인 라우터는 여기에 include_router로 등록한다.
v1_routers = APIRouter(prefix="/api/v1")
# 로그인 기능이 필요해지면 아래 줄의 주석을 해제한다 (auth_kit/README.md 참고).
# v1_routers.include_router(auth_router)
