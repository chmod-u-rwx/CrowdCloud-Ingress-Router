from dataclasses import dataclass
from typing import Dict,Any

@dataclass
class JobCache:
    job_id: str
    repo_link: str
    path: str
    query_params: Dict[str, Any]
    body: Any
    headers: Dict[str, str]
    reward: float