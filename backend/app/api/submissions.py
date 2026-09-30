from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.submission import SubmissionCreate, SubmissionDecision, SubmissionRead
from app.services.submissions import (
    InvalidTransition,
    RoleNotAllowed,
    SubmissionNotFound,
    create_submission,
    decide_submission,
    list_submissions,
)

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _call_service(action):
    try:
        return action()
    except RoleNotAllowed as exc:
        raise HTTPException(status_code=403, detail=exc.detail) from exc
    except SubmissionNotFound as exc:
        raise HTTPException(status_code=404, detail=exc.detail) from exc
    except InvalidTransition as exc:
        raise HTTPException(status_code=409, detail=exc.detail) from exc


@router.post("", response_model=SubmissionRead, status_code=201)
def create(
    data: SubmissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubmissionRead:
    return _call_service(lambda: create_submission(db, user, data))


@router.get("", response_model=list[SubmissionRead])
def list_all(
    status: Literal["pending", "approved", "rejected"] | None = None,
    mine: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SubmissionRead]:
    return list_submissions(db, user, status, mine)


@router.patch("/{submission_id}", response_model=SubmissionRead)
def decide(
    submission_id: int,
    decision: SubmissionDecision,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubmissionRead:
    return _call_service(
        lambda: decide_submission(db, user, submission_id, decision)
    )
