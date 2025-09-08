from typing import List, TypedDict
from uuid import UUID

class Job(TypedDict):
    job_id: UUID

class JobCache(Job):
    reward: float

class Worker(TypedDict):
    worker_id: UUID
    master_id: UUID
    cpu: float
    memory: float
    job_slot: float
    status: str
    code_runtime: float
    latency: float
    job_cache: List[JobCache]

class MaxValues(TypedDict):
    cpu: float
    job_slot: float
    runtime: float
    latency: float