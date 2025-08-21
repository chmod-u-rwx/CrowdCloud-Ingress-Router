from router import Router
from worker import Worker

"""
GO TO: router.py
       worker.py

for detailed explanations!

THIS IS JUST A PROTOTYPE SIMULATION FOR ME TO UNDERSTAND
HOW THE BANDIT ALGORITHM WORKS IT IS NOT ONE IS TO ONE
OF CMAB BUT A VARIANT CALLED GREEDY EPSILON
"""
# Reward is just "job success(1) or job failure(0)"
job_array = [
    {"job_id": 1, "name": "Job1", "reward": None},
    {"job_id": 2, "name": "Job2", "reward": None},
    {"job_id": 3, "name": "Job3", "reward": None},
    {"job_id": 4, "name": "Job4", "reward": None},
    {"job_id": 5, "name": "Job5", "reward": None},
    {"job_id": 6, "name": "Job6", "reward": None},
    {"job_id": 7, "name": "Job7", "reward": None},
    {"job_id": 8, "name": "Job8", "reward": None},
    {"job_id": 9, "name": "Job9", "reward": None},
    {"job_id": 10, "name": "Job10", "reward": None},
    {"job_id": 11, "name": "Job11", "reward": None},
    {"job_id": 12, "name": "Job12", "reward": None},
]

def init_worker_nodes():
    worker_arr = [Worker(x)for x in range(3)]
    
    for x in worker_arr:
        print(f"------------- Worker -------------")
        for attr, value in x.__dict__.items():
            print(f"{attr}: {value}")
    
    return worker_arr

def main():
    workers = init_worker_nodes()
    router = Router(workers, 0.25)

    for job in job_array:
        router.assign_job(job)
    
    for x in workers:
        print(f"------------- Worker Updated -------------")
        for attr, value in x.__dict__.items():
            print(f"{attr}: {value}")

if __name__ == "__main__":
    main()
