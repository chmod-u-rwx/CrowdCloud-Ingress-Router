import gymnasium as gym
from gymnasium import spaces
import numpy as np
from utils.context_vector import build_context_vector
from src.router import Router

class RouterEnv(gym.Env):
    def __init__(self, router: Router, jobs, max_values):
        super().__init__()
        self.router = router
        self.jobs = jobs
        self.max_values = max_values

        self.action_space = spaces.Discrete(len(router.workers))

        ctx_size = 7
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(len(router.workers) * ctx_size,), dtype=np.float32
        )

        self.current_job_indx = 0
    
    def reset(self, *, seed=None):
        self.current_job_indx = 0
        super().reset(seed=seed)

        observation = self._get_obs()
        return observation, {}

    def step(self, action):
        job = self.jobs[self.current_job_indx]
        worker = self.router.workers[action]

        if worker["status"] == "STOPPED":
            reward = -1.0 
            observation = self._get_obs()
            terminated = False
            truncated = False
            return observation, reward, terminated, truncated, {}
    
        reward = self._calculate_reward(worker, job)
        self.router.update_reward(worker["worker_id"], job["job_id"], reward)

        self.current_job_indx += 1
        terminated = self.current_job_indx >= len(self.jobs)
        truncated = False

        observation = self._get_obs() if not terminated else self._zeros_obs()

        return observation, reward, terminated, truncated, {}

    def _get_obs(self):
        if self.current_job_indx >= len(self.jobs):
            return self._zeros_obs()

        job = self.jobs[self.current_job_indx]

        vectors = [
            build_context_vector(worker, job, self.max_values)
            for worker in self.router.workers
        ]
        return np.concatenate(vectors, dtype=np.float32)

    def _zeros_obs(self):
        shape = self.observation_space.shape
        assert shape is not None
        return np.zeros(shape, dtype=np.float32)

    def _calculate_reward(self, worker, job):
        reward = 0.0
        if any(past["job_id"] == job["job_id"] for past in worker.get("job_cache", [])):
            reward += 2.0
        reward += worker["cpu"] * 0.1
        reward -= worker.get("latency", 0) * 0.01
        return reward
