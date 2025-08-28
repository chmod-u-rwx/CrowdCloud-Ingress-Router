# Smart-Routing-System
This repository is for the development of a smart routing system for Crowd Cloud. The routing system will be made using the Contextual Multi-Armed Bandit Algorithm partnered by Reinforcement Learning


NOTE ====================
Worker attr:
    worker_id: str
    master_id: str
    cpu: int
    memory: int
    job_slot: int
    status: str            
    code_runtime: str
    job_cache: List[JobCache]
    latency: int

job attr:
    job_id: str
    repo_link: str
    path: str
    query_params: Dict[str, Any]
    body: Any
    headers: Dict[str, str]
    reward: int (only for jobcaches)