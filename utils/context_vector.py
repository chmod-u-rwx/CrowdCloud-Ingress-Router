import numpy as np
import numpy.typing as npt
from src.type_dict import Worker, Job, MaxValues


def build_context_vector(worker: Worker, job: Job, max_values: MaxValues) -> npt.NDArray[np.float32]:
    """
    Build a normalized context vector for RL agent.

    :param worker: Worker dictionary
    :param job: Job dictionary
    :param max_values: Dictionary with max values for normalization
    :return: np.ndarray context vector (dtype float32)
    """

    cpu_norm: float = worker["cpu"] / max_values["cpu"]
    slot_norm: float = worker["job_slot"] / max_values["job_slot"]
    runtime_norm: float = worker["code_runtime"] / max_values["runtime"]
    latency_norm: float = worker["latency"] / max_values["latency"]

    cache_hit: float = 1.0 if any(
        past_job["job_id"] == job["job_id"]
        for past_job in worker.get("job_cache", [])
    ) else 0.0

    status: str = worker.get("status", "STOPPED")
    if status in ("STARTED", "RUNNING"):
        is_active: float = 1.0
        can_accept: float = 1.0 if worker["job_slot"] > 0 else 0.0
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
