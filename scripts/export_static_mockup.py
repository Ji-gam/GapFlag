"""Jinja2/FastAPI 목업을 Netlify용 정적 HTML로 내보낸다.

Netlify는 정적/서버리스 호스팅이고 이 앱은 FastAPI 상시 서버라 그대로는 배포가 안 된다.
데모 목업 3화면(검색/매트릭스/근거카드)만 스냅샷 떠서 dist/ 아래 저장한다.
성분이 carprofen(dog) 하나뿐인 MVP라 쿼리스트링 링크를 폴더형 경로로 치환한다.
"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

DIST = Path(__file__).resolve().parent.parent / "dist"

PAGES = {
    "index.html": "/",
    "matrix/index.html": "/matrix?ingredient=carprofen&species=dog",
    "compound/carprofen/index.html": "/compound/carprofen?species=dog",
}

REPLACEMENTS = [
    ("/matrix?ingredient=carprofen&species=dog", "/matrix/"),
    ("/compound/carprofen?species=dog", "/compound/carprofen/"),
]


def main() -> None:
    client = TestClient(app)
    for rel_path, route in PAGES.items():
        html = client.get(route).text
        for old, new in REPLACEMENTS:
            html = html.replace(old, new)
        out = DIST / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
