from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core import config
from app.services import cmp_mock, scr_score

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory=config.TEMPLATE_DIR)


@router.get("/", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "") -> HTMLResponse:
    results = cmp_mock.search_compounds(q)
    return templates.TemplateResponse(request, "search.html", {"query": q, "results": results})


def _score(compound: dict) -> dict:
    risk = {k: (v["value"], cmp_mock.weight_for(k)) for k, v in compound["risk"].items()}
    opportunity = {k: (v["value"], cmp_mock.weight_for(k)) for k, v in compound["opportunity"].items()}
    return scr_score.calc_risk_opportunity(risk, opportunity)


@router.get("/matrix", response_class=HTMLResponse)
async def matrix_page(request: Request, ingredient: str, species: str) -> HTMLResponse:
    compound = cmp_mock.get_compound(ingredient, species)
    if compound is None:
        return templates.TemplateResponse(
            request,
            "search.html",
            {"query": ingredient, "results": [], "error": f"'{ingredient}' 성분을 찾을 수 없습니다."},
        )
    return templates.TemplateResponse(request, "matrix.html", {"compound": compound, "score": _score(compound)})


@router.get("/compound/{ingredient}", response_class=HTMLResponse)
async def detail_page(request: Request, ingredient: str, species: str) -> HTMLResponse:
    compound = cmp_mock.get_compound(ingredient, species)
    if compound is None:
        return templates.TemplateResponse(
            request,
            "search.html",
            {"query": ingredient, "results": [], "error": f"'{ingredient}' 성분을 찾을 수 없습니다."},
        )
    return templates.TemplateResponse(request, "detail.html", {"compound": compound, "score": _score(compound)})
