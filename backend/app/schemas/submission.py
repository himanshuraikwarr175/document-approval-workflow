from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubmissionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1)

    @field_validator("title", "body")
    @classmethod
    def reject_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    status: str
    submitter_id: int
    reviewer_note: str | None
    created_at: datetime
    updated_at: datetime
