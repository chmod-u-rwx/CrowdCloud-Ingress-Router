from typing import List, Dict,Any
from uuid import UUID
from .utils.max_value_calc import compute_max_values
from .models.type_dict import Worker, JobCache, Job

class BaseRouter:
    def __init__(self) -> None:
        """
        AI Router for selecting workers based on Contextual Multi-Armed Bandit (CMAB).
        """
        self.workers: List[Worker] = []
        self.job_cache: List[Job] = []

        self.cpu_multiplier: float = 0.4
        self.memory_multiplier: float = 0.3
        self.jobslot_multiplier: float = 0.1
        self.runtime_multiplier: float = -0.1   # negative because lower runtime is better
        self.latency_multiplier: float = -0.1   # negative because lower latency is better
        self.status_bonus: Dict[str, float] = {
            "RUNNING": 0.5,
            "STARTED": 1.0,
            "STOPPED": -1.0
        }

    def select_worker(self, job: Job) -> Dict[str, Any]:
        """
        Select a worker based on combined job cache reward and hardware context score.
        Workers with previous job experience get higher weight.
        """
        if not self.workers:
            raise ValueError("No workers available right now uwu")

        current_job: UUID = job["job_id"]

        def get_worker_score(worker: Worker) -> float:
            hw_score: float = (
                (worker["cpu"] * self.cpu_multiplier) +
                (worker["memory"] * self.memory_multiplier) +
                (worker["job_slot"] * self.jobslot_multiplier) +
                (worker["code_runtime"] * self.runtime_multiplier) +
                (worker["latency"] * self.latency_multiplier)
            )
            hw_score += self.status_bonus.get(worker["status"], 0.0)

            reward_score: float = 0.0
            for past_job in worker.get("job_cache", []):
                if past_job["job_id"] == current_job:
                    reward_score = past_job.get("reward", 0.0) or 0.0
                    break

            combined_score: float = 0.7 * reward_score + 0.3 * hw_score
            return combined_score

        best_worker: Worker = max(self.workers, key=get_worker_score)
        return {"master_id": best_worker["master_id"], "worker_id": best_worker["worker_id"]}

    def update_worker_data(self, worker_list: List[Worker]) -> None:  # heartbeat
        """
        Update the internal worker context list with the latest data.
        Validates that each worker has the required fields.

        :param worker_list: List of worker context dicts (hardware info/status).
        """
        required_attr = {"worker_id", "master_id", "cpu", "memory", "job_slot", "status", "code_runtime", "latency"}
        valid_workers: List[Worker] = []

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
                worker["job_cache"] = []

            valid_workers.append(worker)

        self.workers = valid_workers
        if self.workers:
            self.max_values = compute_max_values(self.workers)  # type: ignore[name-defined]

    def update_reward(self, worker_id: UUID, job_id: UUID, reward: float) -> None:
        for worker in self.workers:
            if worker["worker_id"] == worker_id:
                cache: list[JobCache] = worker.setdefault("job_cache", [])

                for past in cache:
                    if past["job_id"] == job_id:
                        past["reward"] = reward
                        return

                cache.append({"job_id": job_id, "reward": reward})
                return
