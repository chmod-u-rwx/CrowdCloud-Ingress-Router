from typing import List, Dict

def compute_max_values(workers: List[Dict]) -> Dict[str, float]:
    if not workers:
        raise ValueError("Worker list is empty!")

    max_cpu = max(worker["cpu"] for worker in workers)
    max_slot = max(worker["job_slot"] for worker in workers)
    max_runtime = max(worker["code_runtime"] for worker in workers)
    max_latency = max(worker["latency"] for worker in workers)

    return {
        "cpu": max_cpu,
        "job_slot": max_slot,
        "runtime": max_runtime,
        "latency": max_latency,
    }