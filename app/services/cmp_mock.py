"""Mock MVP용 성분 데이터. 실제 API 연동 전까지 고정 dict 사용 (docs/STEP4-2_MockMVP_PRD_NextJS.md §6~7)."""

_WEIGHTS = {"r1": 25.0, "r2": 25.0, "r3": 25.0, "r4": 25.0, "o1": 40.0, "o2": 30.0, "o3": 30.0}

_COMPOUNDS: dict[tuple[str, str], dict] = {
    ("carprofen", "dog"): {
        "ingredient_name": "carprofen",
        "species": "dog",
        "risk": {
            "r1": {"value": None, "label": "임상 중단 이력", "source_name": "Open Targets", "summary": "사람 임상 중단 이력 확인 안 됨", "source_url": "https://platform.opentargets.org/"},
            "r2": {"value": 45.0, "label": "동물 이상반응", "source_name": "openFDA ADAE", "summary": "최근 보고 이상반응 다수", "source_url": "https://open.fda.gov/apis/animalandveterinary/event/"},
            "r3": {"value": 20.0, "label": "승인·철회 이력", "source_name": "FDA Green Book", "summary": "승인 유지 중", "source_url": "#"},
            "r4": {"value": None, "label": "특허 밀집도", "source_name": "EPO OPS", "summary": "특허 데이터 미확인", "source_url": "#"},
        },
        "opportunity": {
            "o1": {"value": 60.0, "label": "문헌 희소성", "source_name": "Europe PMC", "summary": "관련 문헌 다소 적음", "source_url": "https://europepmc.org/"},
            "o2": {"value": None, "label": "임상 부재", "source_name": "ClinicalTrials.gov", "summary": "임상시험 등록 정보 미확인", "source_url": "#"},
            "o3": {"value": 0.0, "label": "미승인 여부", "source_name": "FDA Green Book", "summary": "이미 승인됨", "source_url": "#"},
        },
    },
}


def list_compounds() -> list[dict]:
    return [{"ingredient_name": name, "species": species} for name, species in _COMPOUNDS]


def search_compounds(query: str) -> list[dict]:
    q = query.strip().lower()
    if not q:
        return list_compounds()
    return [c for c in list_compounds() if q in c["ingredient_name"].lower()]


def get_compound(ingredient_name: str, species: str) -> dict | None:
    return _COMPOUNDS.get((ingredient_name.strip().lower(), species.strip().lower()))


def weight_for(component_key: str) -> float:
    return _WEIGHTS[component_key]
