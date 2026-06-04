"""Configuration-only invigilation payment rate rule routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import schemas
from auth_utils import require_admin, require_staff_or_admin
from database import get_db
from services.invigilation_rate_rule_service import (
    activate_rate_rule,
    archive_rate_rule,
    create_rate_rule,
    get_simple_rates,
    list_rate_rules,
    save_simple_rates,
    update_rate_rule,
)

router = APIRouter()


@router.get("/simple-rates", response_model=schemas.InvigilationSimpleRatesResponse)
def get_invigilation_simple_rates(
    db: Session = Depends(get_db),
    _current_user=Depends(require_staff_or_admin),
):
    return get_simple_rates(db)


@router.put("/simple-rates", response_model=schemas.InvigilationSimpleRatesResponse)
def put_invigilation_simple_rates(
    payload: schemas.InvigilationSimpleRateUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return save_simple_rates(db, payload, actor_id=getattr(current_user, "id", None))


@router.get("/rate-rules", response_model=schemas.InvigilationRateRuleListResponse)
def list_invigilation_rate_rules(
    db: Session = Depends(get_db),
    _current_user=Depends(require_staff_or_admin),
):
    return list_rate_rules(db)


@router.post("/rate-rules", response_model=schemas.InvigilationRateRuleMutationResponse)
def create_invigilation_rate_rule(
    payload: schemas.InvigilationRateRuleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return create_rate_rule(db, payload, actor_id=getattr(current_user, "id", None))


@router.put("/rate-rules/{rate_rule_id}", response_model=schemas.InvigilationRateRuleMutationResponse)
def update_invigilation_rate_rule(
    rate_rule_id: int,
    payload: schemas.InvigilationRateRuleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return update_rate_rule(db, rate_rule_id, payload, actor_id=getattr(current_user, "id", None))


@router.post("/rate-rules/{rate_rule_id}/activate", response_model=schemas.InvigilationRateRuleMutationResponse)
def activate_invigilation_rate_rule(
    rate_rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return activate_rate_rule(db, rate_rule_id, actor_id=getattr(current_user, "id", None))


@router.post("/rate-rules/{rate_rule_id}/archive", response_model=schemas.InvigilationRateRuleMutationResponse)
def archive_invigilation_rate_rule(
    rate_rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return archive_rate_rule(db, rate_rule_id, actor_id=getattr(current_user, "id", None))
