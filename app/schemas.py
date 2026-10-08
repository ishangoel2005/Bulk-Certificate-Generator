from typing import List

from pydantic import BaseModel, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class JobCreate(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=200)
    event_date: str = Field(..., min_length=1, max_length=50)

    recipients: List[RecipientCreate] = Field(
        ...,
        min_length=1,
        max_length=500
    )


class CertificateSummary(BaseModel):
    id: int
    recipient_name: str
    recipient_email: str
    status: str
    error_message: str | None = None


class JobResponse(BaseModel):
    job_id: int
    status: str
    total: int
    successful: int
    failed: int
    progress: float
    certificates: List[CertificateSummary]