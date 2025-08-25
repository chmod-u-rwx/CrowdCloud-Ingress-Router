from dataclasses import dataclass
from typing import List
from tests.dataclasses.jobcache import JobCache

@dataclass
class WorkerContext:
    worker_id: str
    master_id: str
    cpu: int
    memory: int
    job_slot: int
    status: str            
    code_runtime: str
    job_cache: List[JobCache]