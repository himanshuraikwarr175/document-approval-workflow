from sqlalchemy.orm import Session

from app.models import Submission, User
from app.schemas.submission import SubmissionCreate, SubmissionDecision


class RoleNotAllowed(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class SubmissionNotFound(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


class InvalidTransition(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail


def create_submission(db: Session, user: User, data: SubmissionCreate) -> Submission:
    if user.role != "submitter":
        raise RoleNotAllowed("Only a submitter can create a submission")

    submission = Submission(
        title=data.title,
        body=data.body,
        status="pending",
        submitter_id=user.id,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
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
