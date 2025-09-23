from stable_baselines3 import PPO
from typing import List, Dict
from uuid import UUID
from .models.type_dict import Job, Worker, MaxValues
from stable_baselines3 import PPO
from .base_router import BaseRouter
from .routerenv import RouterEnv
from .utils.max_value_calc import compute_max_values
from .utils.context_vector import build_context_vector
import numpy as np

class Router:
    """
    Runtime wrapper for a trained PPO model router.
    Functions for both trained router and PPO model for training and usage.
    """

    def __init__(self, ppo_model_path: str):
        self.base_router = BaseRouter()
        self.max_values: MaxValues = {} # type: ignore
        self.env: RouterEnv | None = None
        self.model = PPO.load(ppo_model_path) # type: ignore

    def update_worker_data(self, worker_list:List[Worker]):
        """
        Populate/refresh the worker list and compute max_values.
        Must be called before select_workers.
        """
        self.base_router.update_worker_data(worker_list)
        self.max_values = compute_max_values(self.base_router.workers)

        # only to satisfy routerenv init, won't be used
        dummy_jobs: list[Job] = [
            {
                "job_id": UUID(int=0),
            }
        ]
        self.env = RouterEnv(self.base_router, dummy_jobs, self.max_values)

    def select_worker(self, job: Job) -> Dict[str, UUID]:
            """
            Call update_worker_data before running this.
            Select a worker for the given job using the trained PPO model.
            """
            if not self.base_router.workers:
                raise RuntimeError("No workers available. Call update_worker_data first.")
            if self.env is None:
                raise RuntimeError("Environment not initialized. Call update_worker_data first.")

            vectors = [build_context_vector(worker, job, self.max_values)
                    for worker in self.base_router.workers]

            while len(vectors) < 4:
                vectors.append(np.zeros_like(vectors[0]))
            
            obs = np.concatenate(vectors, dtype=np.float32)
            action_array, _ = self.model.predict(obs, deterministic=False) # type: ignore
            action = int(action_array) #type: ignore
            action = min(action, len(self.base_router.workers) - 1)
            worker = self.base_router.workers[action]

            return {"worker_id": worker["worker_id"], "master_id": worker["master_id"]}

router = Router("worker_selector_model.zip")