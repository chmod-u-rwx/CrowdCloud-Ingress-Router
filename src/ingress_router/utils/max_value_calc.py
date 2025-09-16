from typing import List

from ..models.type_dict import Worker, MaxValues

def compute_max_values(workers: List[Worker]) -> MaxValues:
    if not workers:
        raise ValueError("Worker list is empty!")

    return MaxValues(
        cpu=max(worker["cpu"] for worker in workers),
        memory=max(worker["memory"] for worker in workers),
        job_slot=max(worker["job_slot"] for worker in workers),
        runtime=max(worker["code_runtime"] for worker in workers),
        latency=max(worker["latency"] for worker in workers),
    )