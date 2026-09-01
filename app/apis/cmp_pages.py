from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import config
from app.core.db.databases import get_db
from app.services import cmp_mock, cmp_service, scr_score

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory=config.TEMPLATE_DIR)

Db = Annotated[AsyncSession, Depends(get_db)]


@router.get("/", response_class=HTMLResponse)
async def search_page(request: Request, db: Db, q: str = "") -> HTMLResponse:
    db_results = await cmp_service.search_compounds(db, q)
    seen = {(r["ingredient_name"], r["species"]) for r in db_results}
    mock_results = [r for r in cmp_mock.search_compounds(q) if (r["ingredient_name"], r["species"]) not in seen]
    return templates.TemplateResponse(request, "search.html", {"query": q, "results": db_results + mock_results})


def _mock_score(compound: dict) -> dict:
    risk = {k: (v["value"], cmp_mock.weight_for(k)) for k, v in compound["risk"].items()}
    opportunity = {k: (v["value"], cmp_mock.weight_for(k)) for k, v in compound["opportunity"].items()}
    return scr_score.calc_risk_opportunity(risk, opportunity)


async def _lookup(db: AsyncSession, ingredient: str, species: str) -> tuple[dict, dict] | None:
    """DB(build_cache.py로 실제 수집된 성분)를 먼저 보고, 없으면 제출용 mock으로 대체한다."""
    view = await cmp_service.get_compound_view(db, ingredient, species)
    if view is not None:
        return view, view["score"]
    compound = cmp_mock.get_compound(ingredient, species)
    if compound is None:
        return None
    return compound, _mock_score(compound)


@router.get("/matrix", response_class=HTMLResponse)
async def matrix_page(request: Request, db: Db, ingredient: str = "", species: str = "") -> HTMLResponse:
    points = await cmp_service.list_matrix_points(db)
    if not points:
        points = cmp_mock.list_matrix_points()

    highlight = None
    if ingredient and species:
        found = await _lookup(db, ingredient, species)
        if found is None:
            return templates.TemplateResponse(
                request,
                "search.html",
                {"query": ingredient, "results": [], "error": f"'{ingredient}' 성분을 찾을 수 없습니다."},
            )
        highlight = (ingredient.strip().lower(), species.strip().lower())

    return templates.TemplateResponse(request, "matrix.html", {"points": points, "highlight": highlight})


@router.get("/compound/{ingredient}", response_class=HTMLResponse)
async def detail_page(request: Request, db: Db, ingredient: str, species: str) -> HTMLResponse:
    found = await _lookup(db, ingredient, species)
    if found is None:
        return templates.TemplateResponse(
            request,
            "search.html",
            {"query": ingredient, "results": [], "error": f"'{ingredient}' 성분을 찾을 수 없습니다."},
        )
    compound, score = found
    return templates.TemplateResponse(request, "detail.html", {"compound": compound, "score": score})
