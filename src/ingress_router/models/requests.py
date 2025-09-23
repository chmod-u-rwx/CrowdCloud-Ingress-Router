from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from .payloads import JobRequestPayload, JobResponsePayload

class RequestStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class Requests(BaseModel):
    request_id: UUID = Field(...)
    job_id: UUID = Field(...)
    worker_id: UUID = Field(...)
    vm_id: UUID = Field(...)
    request_payload: JobRequestPayload = Field(...)
    response_payload: JobResponsePayload = Field(...)
    status: Optional[RequestStatus] = Field(default=None)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time: float = Field(..., description="Execution time in seconds")
    transaction_id: UUID = Field(..., description="Reference to Job expense")