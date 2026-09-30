from typing import Literal

from fastapi import APIRouter, Depends, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models import User
from app.schemas.submission import SubmissionDecision, SubmissionRead, clean_title
from app.services.submissions import (
    InvalidTransition,
    RoleNotAllowed,
    SubmissionNotFound,
    create_submission,
    decide_submission,
    get_readable_submission,
    list_submissions,
)
from app.storage import MAX_BYTES, InvalidFile, file_path

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
    except InvalidFile as exc:
        raise HTTPException(status_code=422, detail=exc.detail) from exc


@router.post("", response_model=SubmissionRead, status_code=201)
def create(
    file: UploadFile,
    title: str = Form(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SubmissionRead:
    try:
        cleaned_title = clean_title(title)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _call_service(
        lambda: create_submission(
            db,
            user,
            cleaned_title,
            file.filename,
            file.file.read(MAX_BYTES + 1),
        )
    )


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


@router.get("/{submission_id}/file")
def download(
    submission_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> FileResponse:
    def open_file():
        submission = get_readable_submission(db, user, submission_id)
        return submission, file_path(submission.stored_name)

    submission, path = _call_service(open_file)
    return FileResponse(path, filename=submission.original_filename)
