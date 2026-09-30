from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


def clean_title(title: str) -> str:
    title = title.strip()
    if not title or len(title) > 200:
        raise ValueError("Title must be 1 to 200 characters")
    return title


class SubmissionDecision(BaseModel):
    status: Literal["approved", "rejected"]
    note: str | None = None

    @field_validator("note")
    @classmethod
    def blank_note_is_empty(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    original_filename: str
    status: str
    submitter_id: int
    reviewer_note: str | None
    created_at: datetime
    updated_at: datetime
