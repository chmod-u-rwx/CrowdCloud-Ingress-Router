import random
from typing import List
from worker import Worker

"""
This router prototype explores the multi armed bandit algorithm.
The main use of this protoype is for me to learn and understand the most basic version
of the bandit algorithm before moving on to the contextual bandit.

This mostly tackles the epsilon greedy version of MAB in which the router tries to explore each
worker node but exploits the worker node that has the highest success in job_cache(1=success, 0=failure)
"""

class Router:
    def __init__(self, workers: List[Worker], epsilon = 0.1):
        self.workers = workers
        self.epsilon = epsilon

    def select_worker(self):
        """
        Epsilon greedy variant explores workers at random, 
        it is not required to give atleast one job per worker
        """
        if random.random() < self.epsilon:   # Exploration
            return random.choice(self.workers)
        
        """
        When it exploits it finds the worker with the most job successes
        to give its jobs to, all the while still trying to explore other workers
        if some have potential
        """
        return max(self.workers, key=lambda w: w.get_avg_reward()) # Exploitation
    
    def assign_job(self, job: dict):
        """
        This area simulates whe assigning a job and sees if it is a success or a failure,
        The output of the result(reward) of the past job is then added into the past_job_cache
        for the algorithm to use if the worker is a good worker
        """
        selected_worker = self.select_worker()
        reward = random.choice([1,0])

        selected_worker.past_job_cache.append(reward)
        job["reward"] = reward
        print(f"Assigned {job['name']} to {selected_worker.worker_id}, reward={reward}")