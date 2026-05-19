from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
from auth_utils import get_current_user, require_admin
from services.dashboard_service import DashboardService
from policies.dashboard_policy import DashboardPolicy
from validators.dashboard_validator import DashboardValidator
from serializers.dashboard_serializer import DashboardSerializer

router = APIRouter()


@router.get("/", response_model=schemas.DashboardStats)
def get_dashboard(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    semester = DashboardValidator.validate_semester(semester)
    academic_year = DashboardValidator.validate_academic_year(academic_year)
    DashboardPolicy.require_dashboard_access(current_user)

    stats = DashboardService.get_dashboard_stats(db, semester, academic_year, current_user)
    return schemas.DashboardStats(**stats)


@router.get("/analytics")
def get_analytics(
    semester: str = "2",
    academic_year: str = "2568",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin),
):
    from auth_utils import get_effective_role
    DashboardPolicy.require_analytics_access(current_user)

    semester = DashboardValidator.validate_semester(semester)
    academic_year = DashboardValidator.validate_academic_year(academic_year)

    data = DashboardService.get_analytics(db, semester, academic_year)
    user_role = get_effective_role(current_user)
    return DashboardSerializer.serialize_analytics(data)
