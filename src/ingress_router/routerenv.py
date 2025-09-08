from typing import List, Tuple, Dict, Any
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import numpy.typing as npt

from .router import Router
from .type_dict import Worker, Job, MaxValues
from .utils.context_vector import build_context_vector


class RouterEnv(gym.Env[npt.NDArray[np.float32], int]):
    """
    A Gymnasium environment for training a Router agent.
    Each observation is a concatenated context vector for all workers,
    given the current job.
    """

    metadata = {"render_modes": []}

    def __init__(self, router: Router, jobs: List[Job], max_values: MaxValues) -> None:
        super().__init__()
        self.router: Router = router
        self.jobs: List[Job] = jobs
        self.max_values: MaxValues = max_values

        # Each worker is an action
        self.action_space = spaces.Discrete(len(router.workers)) # type: ignore

        ctx_size: int = 7
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(len(router.workers) * ctx_size,), dtype=np.float32
        )

        self.current_job_indx: int = 0

    def reset(self, *, seed: int | None = None, options: Dict[str, Any] | None = None) -> Tuple[npt.NDArray[np.float32], Dict[str, Any]]:
        self.current_job_indx = 0
        super().reset(seed=seed)

        observation = self._get_obs()
        return observation, {}

    def step(self, action: int) -> Tuple[npt.NDArray[np.float32], float, bool, bool, Dict[str, Any]]:
        job: Job = self.jobs[self.current_job_indx]
        worker: Worker = self.router.workers[action]

        if worker["status"] == "STOPPED":
            reward: float = -1.0
            observation = self._get_obs()
            terminated: bool = False
            truncated: bool = False
            return observation, reward, terminated, truncated, {}

        reward = self._calculate_reward(worker, job)
        self.router.update_reward(worker["worker_id"], job["job_id"], reward)

        self.current_job_indx += 1
        terminated: bool = self.current_job_indx >= len(self.jobs)
        truncated: bool = False

        observation = self._get_obs() if not terminated else self._zeros_obs()
        return observation, reward, terminated, truncated, {}

    def _get_obs(self) -> npt.NDArray[np.float32]:
        if self.current_job_indx >= len(self.jobs):
            return self._zeros_obs()

        job: Job = self.jobs[self.current_job_indx]

        vectors = [
            build_context_vector(worker, job, self.max_values)
            for worker in self.router.workers
        ]
        return np.concatenate(vectors, dtype=np.float32)

    def _zeros_obs(self) -> npt.NDArray[np.float32]:
        shape = self.observation_space.shape
        assert shape is not None
        return np.zeros(shape, dtype=np.float32)

    def _calculate_reward(self, worker: Worker, job: Job) -> float:
        reward: float = 0.0
        if any(past["job_id"] == job["job_id"] for past in worker.get("job_cache", [])):
            reward += 2.0
        reward += worker["cpu"] * 0.1
        reward -= worker["latency"] * 0.01
        return reward
