from __future__ import annotations
from typing import Any, Dict, List, Union, cast
from routerenv import RouterEnv
import pandas as pd
import json
import numpy as np
import numpy.typing as npt
from uuid import UUID

from .type_dict import Job
from .router import Router, Worker, Job
from .utils.max_value_calc import compute_max_values

workers_data_file: str = "data/worker.xlsx"
jobs_data_file: str = "data/jobs.xlsx"


def parse_job_cache(value: Union[str, List[Any], List[Dict[str, Any]], None]) -> List[Job]:
    """
    Normalize job_cache values from Excel into a list of {"job_id": str}.
    Handles JSON strings, comma-separated, single strings, and lists.
    """
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                result: List[Job] = []
                for j in parsed: # type: ignore
                    if isinstance(j, str):
                        result.append(Job(job_id=UUID(j)))
                    elif isinstance(j, dict):
                        j_dict = cast(dict[str, Any], j)
                        result.append(Job(job_id=UUID(str(j_dict["job_id"]))))
                return result
        except json.JSONDecodeError:
            pass

        if "," in value:
            return [Job(job_id=UUID(j.strip())) for j in value.split(",")]

        return [Job(job_id=UUID(value.strip()))]

    if isinstance(value, list):
        jobs: List[Job] = []
        for j in value:
            if isinstance(j, str):
                jobs.append(Job(job_id=UUID(j)))
            elif isinstance(j, dict):
                j_dict = cast(dict[str, Any], j)
                jobs.append(Job(job_id=UUID(str(j_dict["job_id"]))))
        return jobs

    return []


# --- Load data ---
workers_df: pd.DataFrame = pd.read_excel(workers_data_file) # type: ignore
jobs_df: pd.DataFrame = pd.read_excel(jobs_data_file) # type: ignore

workers_df["job_cache"] = workers_df["job_cache"].apply(parse_job_cache) #type: ignore

workers: List[Worker] = workers_df.to_dict(orient="records")  # type: ignore
jobs: List[Job] = jobs_df.to_dict(orient="records")  # type: ignore


# --- Router + Environment ---
router = Router()
router.update_worker_data(workers)  # populates router.workers

env = RouterEnv(router, jobs, compute_max_values(workers))

obs: npt.NDArray[np.float32]
obs, _ = env.reset()

ctx_size: int = 7
print("Initial observation by worker:")
for i, worker in enumerate(router.workers):
    start = i * ctx_size
    end = start + ctx_size
    worker_obs: npt.NDArray[np.float32] = obs[start:end]
    print(f"  {worker['worker_id']}: {worker_obs}")


# --- RL Training ---
# model = PPO("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=5000) # type:ignore
# model.save("worker_selector_model")

print("Training finished and model saved.")
