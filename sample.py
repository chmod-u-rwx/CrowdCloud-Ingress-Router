# example_run.py
from uuid import uuid4
from typing import List
from src.ingress_router.router import Router
from src.ingress_router.models.type_dict import Worker, Job 

# -----------------------------
# Step 1: Initialize Router with trained PPO model
# -----------------------------
ppo_model_path = "worker_selector_model"
router = Router(ppo_model_path)

# -----------------------------
# Step 2: Define workers
# -----------------------------
workers: List[Worker] = [
    {
        "worker_id": uuid4(),
        "master_id": uuid4(),
        "cpu": 0.8,
        "memory": 0.5,
        "job_slot": 1,
        "status": "RUNNING",
        "code_runtime": 2.0,
        "latency": 0.1,
        "job_cache": []
    },
    {
        "worker_id": uuid4(),
        "master_id": uuid4(),
        "cpu": 1.0,
        "memory": 0.7,
        "job_slot": 2,
        "status": "STARTED",
        "code_runtime": 1.5,
        "latency": 0.05,
        "job_cache": []
    },
    {
        "worker_id": uuid4(),
        "master_id": uuid4(),
        "cpu": 0.5,
        "memory": 1.0,
        "job_slot": 0,
        "status": "STOPPED",
        "code_runtime": 2.5,
        "latency": 0.2,
        "job_cache": []
    },
    {
        "worker_id": uuid4(),
        "master_id": uuid4(),
        "cpu": 0.9,
        "memory": 0.9,
        "job_slot": 1,
        "status": "RUNNING",
        "code_runtime": 1.0,
        "latency": 0.1,
        "job_cache": []
    },
]

router.update_worker_data(workers)

# -----------------------------
# Step 3: Define incoming jobs
# -----------------------------
jobs: List[Job] = [
    {"job_id": uuid4()},
    {"job_id": uuid4()},
    {"job_id": uuid4()},
]

# -----------------------------
# Step 4: Select workers for jobs
# -----------------------------
for i, job in enumerate(jobs):
    selected_worker = router.select_worker(job)
    print(f"Job {i + 1} -> Worker selected: {selected_worker}")

    router.base_router.update_reward(
        worker_id=selected_worker["worker_id"],
        job_id=job["job_id"],
        reward=1.0  # Example reward
    )

# -----------------------------
# Step 5: Inspect worker job caches
# -----------------------------
for worker in router.base_router.workers:
    print(f"Worker {worker['worker_id']} job_cache: {worker['job_cache']}")