from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime, timezone
from enum import Enum

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class Transaction(BaseModel):
    transaction_id: UUID = Field(..., description="Reference to the Requests model")
    request_id: UUID = Field(..., description="Reference to the Requests model")
    job_id: UUID = Field(...)
    worker_id: UUID = Field(...)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cost_ram: float = Field(..., description="current cost of RAM (per second)")
    cost_cpu: float = Field(..., description="current cost of CPU (per second)")
    execution_time: float = Field(..., description="Execution time in seconds")
    total_cost: float = Field(...)
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
