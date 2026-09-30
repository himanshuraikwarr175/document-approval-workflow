from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.submission import SubmissionCreate, SubmissionRead
from app.services.submissions import RoleNotAllowed, create_submission, list_submissions

router = APIRouter(prefix="/submissions", tags=["submissions"])


@router.post("", response_model=SubmissionRead, status_code=201)
def create(
    data: SubmissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubmissionRead:
    try:
        submission = create_submission(db, user, data)
    except RoleNotAllowed as exc:
        raise HTTPException(status_code=403, detail=exc.detail) from exc
    return submission


@router.get("", response_model=list[SubmissionRead])
def list_all(
    status: Literal["pending", "approved", "rejected"] | None = None,
    mine: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[SubmissionRead]:
    return list_submissions(db, user, status, mine)
