# 도메인 모델을 여기에 임포트해 Base.metadata에 등록한다(Alembic autogenerate 대상).
import app.models.cmp_models  # noqa: F401  # Compound/CompoundScore/CompoundEvidence/SpeciesAlert
import auth_kit.models  # noqa: F401  # users/social_accounts/terms_agreements 등 (auth_kit 소유)
from app.models.base import Base

__all__ = [
    "Base",
]
