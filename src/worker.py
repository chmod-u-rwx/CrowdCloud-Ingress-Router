from enum import Enum
import random

"""
The only important thing to take note from this file is the "past_job_cache"
since its the only deciding factor (as of now) for the algorithm to check.

Since our algorithm will be Contextual Multi-Armed Bandit(CMAB) the attributes of
the worker node wil play a major role in deciding which worker is best for the job.
"""
class Status(Enum):
    STOPPED = 0
    STARTED = 1
    RUNNING = 2

class Worker:
    def __init__(self, worker_id):
        self.worker_id = f"worker_{worker_id}"
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.job_slot = 0
        self.status = Status.STOPPED
        self.past_job_cache = []

        """
        Let's assume that the worker has a hidden attribute called
        success_rate, where it calculates all of the attributes of
        our worker. This is where the AI learns from.
        """

        self.randomize()

    def randomize(self):
        self.cpu_usage = round(random.uniform(0.1, 1.0), 2)
        self.memory_usage = round(random.uniform(0.1, 1.0), 2)
        self.job_slot = random.randint(1, 5)
        self.status = Status(random.choice(list(Status)))

    """
    Calculates the average reward to send to the router
    if it has the highest reward out of all workers,
    router will exploit that worker
    """
    def get_avg_reward(self):
        if not self.past_job_cache:
            return 0
        return sum(self.past_job_cache) / len(self.past_job_cache)