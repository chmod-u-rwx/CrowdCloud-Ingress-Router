import numpy as np

def build_context_vector(worker: dict, job: dict, max_values: dict) -> np.ndarray:
    """
    Build a normalized context vector for RL agent.

    :param worker: Worker dictionary
    :param job: Job dictionary
    :param max_values: Dictionary with max values for normalization
    :return: np.ndarray context vector
    """

    cpu_norm = worker["cpu"] / max_values["cpu"]
    slot_norm = worker["job_slot"] / max_values["job_slot"]
    runtime_norm = worker["code_runtime"] / max_values["runtime"]
    latency_norm = worker["latency"] / max_values["latency"]

    cache_hit = 1.0 if any(past_job["job_id"] == job["job_id"]
                           for past_job in worker.get("job_cache", [])) else 0.0

    status = worker.get("status", "STOPPED")
    if status == "STARTED":
        is_active = 1.0
        can_accept = 1.0 if worker["job_slot"] > 0 else 0.0
    elif status == "RUNNING":
        is_active = 1.0
        can_accept = 1.0 if worker["job_slot"] > 0 else 0.0
    else:
        is_active = 0.0
        can_accept = 0.0

    return np.array([
        cpu_norm,
        slot_norm,
        runtime_norm,
        latency_norm,
        cache_hit,
        is_active,
        can_accept,
    ], dtype=np.float32)
