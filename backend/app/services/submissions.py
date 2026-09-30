from sqlalchemy.orm import Session

from app.models import Submission, User
from app.schemas.submission import SubmissionDecision
from app.storage import InvalidFile, delete_stored_file, file_path, save_upload


class RoleNotAllowed(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class SubmissionNotFound(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class InvalidTransition(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


def create_submission(
    db: Session,
    user: User,
    title: str,
    filename: str | None,
    data: bytes,
) -> Submission:
    if user.role != "submitter":
        raise RoleNotAllowed("Only a submitter can create a submission")

    original_filename, stored_name = save_upload(filename, data)
    submission = Submission(
        title=title,
        original_filename=original_filename,
        stored_name=stored_name,
        status="pending",
        submitter_id=user.id,
    )
    try:
        db.add(submission)
        db.commit()
        db.refresh(submission)
    except Exception:
        delete_stored_file(stored_name)
        raise
    return submission


def list_submissions(
    db: Session,
    user: User,
    status: str | None,
    mine: bool,
) -> list[Submission]:
    query = db.query(Submission)
    if user.role == "submitter" or mine:
        query = query.filter(Submission.submitter_id == user.id)
    if status is not None:
        query = query.filter(Submission.status == status)
    return query.order_by(Submission.created_at.desc(), Submission.id.desc()).all()


def decide_submission(
    db: Session,
    user: User,
    submission_id: int,
    decision: SubmissionDecision,
) -> Submission:
    if user.role != "reviewer":
        raise RoleNotAllowed("Only a reviewer can approve or reject a submission")

    submission = db.get(Submission, submission_id)
    if submission is None:
        raise SubmissionNotFound("Submission not found")
    if submission.status != "pending":
        raise InvalidTransition("Only a pending submission can change status")

    submission.status = decision.status
    submission.reviewer_note = decision.note
    db.commit()
    db.refresh(submission)
    return submission


def get_readable_submission(db: Session, user: User, submission_id: int) -> Submission:
    submission = db.get(Submission, submission_id)
    if submission is None:
        raise SubmissionNotFound("Submission not found")
    if user.role == "submitter" and submission.submitter_id != user.id:
        raise RoleNotAllowed("You can only open your own documents")
    if not submission.stored_name:
        raise SubmissionNotFound("This submission has no file")
    try:
        file_path(submission.stored_name)
    except InvalidFile as exc:
        raise SubmissionNotFound("File not found") from exc
    return submission
