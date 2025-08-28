from typing import List, Dict, Any
import random  
from utils.context_vector import build_context_vector
from utils.max_value_calc import compute_max_values


class Router:
    def __init__(self, epsilon: float = 0.1):
        """
        AI Router for selecting workers based on Contextual Multi-Armed Bandit (CMAB).
        
        :param workers: list of WorkerContext objects
        :param epsilon: exploration rate (0 < epsilon < 1)
        """
        self.workers: List[Dict[str,Any]] = []
        self.job_cache: List[Dict[str,Any]] = []
        self.epsilon = epsilon

        self.cpu_multiplier = 0.4
        self.memory_multiplier = 0.3
        self.jobslot_multiplier = 0.1
        self.runtime_multiplier = -0.1   # negative because lower runtime is better
        self.latency_multiplier = -0.1   # negative because lower latency is better
        self.status_bonus = {
            "RUNNING": 1.0,
            "STARTED": 0.5,
            "STOPPED": -1.0
        }

    def select_worker(self, job: dict) -> Dict[str, str]:
        """
        Select a worker for the given job using:
            1. Job cache match (if worker ran same job_id before).
            2. Hardware context ranking (CPU, job slots, runtime).
            3. Epsilon-greedy fallback.
        
        :param job: JobCache object with job details
        :return: chosen WorkerContext
        """
        if not self.workers:
            raise ValueError("No workers available right now uwu")

        for worker in self.workers:
            ctx = build_context_vector(worker, job, self.max_values)
            print(f"[DEBUG] Worker {worker['worker_id']} context: {ctx}")
        
        workers_with_same_job_cache = []
        current_job=job["job_id"]

        for worker in self.workers:
            job_cache = worker.get("job_cache", [])
            for past_job in job_cache:
                if past_job["job_id"] == current_job:
                    if "reward" not in past_job:
                        raise KeyError(f"{past_job} in worker {worker["worker_id"]} is missing reward key")
                    workers_with_same_job_cache.append((worker, past_job["reward"]))
        
        if workers_with_same_job_cache:
            best_worker, _ = max(workers_with_same_job_cache, key=lambda x: x[1])
            return {"master_id": best_worker["master_id"], "worker_id": best_worker["worker_id"]}
        
        def get_worker_hardware_score(worker: Dict[str, Any]) -> float:
            score = (
                (worker["cpu"] * 0.4) +
                (worker["memory"] * 0.3) +
                (worker["job_slot"] * 0.1) +
                (worker["code_runtime"] * -0.1) +
                (worker["latency"] * -0.1)
            )
            score += self.status_bonus.get(worker["status"], 0)
            return score
        
        best_worker = max(self.workers, key=get_worker_hardware_score)

        if random.random() < self.epsilon:
            return random.choice(self.workers)
        return {"master_id": best_worker["master_id"], "worker_id": best_worker["worker_id"]}

    def update_worker_data(self, worker_list: List[Dict[str,Any]]): # heartbeat
        """
        Update the internal worker context list with the latest data.
        Validates that each worker has the required fields.

        :param worker_list: List of worker context dicts (hardware info/status).
        """
        required_attr = {"worker_id", "master_id", "cpu", "memory", "job_slot", "status", "code_runtime", "latency"}
        valid_workers = []

        for worker in worker_list:
            if not required_attr.issubset(worker.keys()):
                print(f"Skipping {worker}, due to missing attributes")
                continue

            try:
                worker["cpu"] = float(worker["cpu"])
                worker["memory"] = float(worker["memory"])
                worker["job_slot"] = float(worker["job_slot"])
                worker["code_runtime"] = float(worker["code_runtime"])
            except (ValueError, TypeError):
                print(f"Skipping {worker}, due to invalid data types")
                continue

            if "job_cache" not in worker:
                worker["job_cache"] = [] # ewan ko sabi ni expert just in case lang daw kaya sundan nalang natin

            valid_workers.append(worker)
        
        self.workers = valid_workers
        self.max_values = compute_max_values(self.workers)

    def update_reward(self, worker_id: str, job_id: str, reward: float):
        for worker in self.workers:
            if worker["worker_id"] == worker_id:
                cache = worker.setdefault("job_cache", [])
                
                for past in cache:
                    if past["job_id"] == job_id:
                        past["reward"] = reward
                        return
                
                cache.append({"job_id": job_id, "reward": reward})
                return