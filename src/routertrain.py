from src.routerenv import RouterEnv
from src.router import Router
from utils.max_value_calc import compute_max_values
from stable_baselines3 import PPO
import pandas as pd
import json

workers_data_file = "data/worker.xlsx"
jobs_data_file = "data/jobs.xlsx"

workers_df = pd.read_excel(workers_data_file)
jobs_df = pd.read_excel(jobs_data_file)

def parse_job_cache(value):
    if isinstance(value, str):
        # Case 1: JSON string (["job_1", "job_2"])
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [{"job_id": j.strip()} if isinstance(j, str) else j for j in parsed]
        except json.JSONDecodeError:
            pass

        # Case 2: Comma separated (job_1, job_2)
        if "," in value:
            return [{"job_id": j.strip()} for j in value.split(",")]

        # Case 3: Single string (job_1)
        return [{"job_id": value.strip()}]

    # Already list of dicts
    if isinstance(value, list):
        if all(isinstance(j, str) for j in value):
            return [{"job_id": j} for j in value]
        return value

    return []

workers_df["job_cache"] = workers_df["job_cache"].apply(parse_job_cache)

workers = workers_df.to_dict(orient='records')
jobs = jobs_df.to_dict(orient='records')

router = Router()
router.update_worker_data(workers) #type: ignore
env = RouterEnv(router, jobs, compute_max_values(workers))

obs, _ = env.reset()

ctx_size = 7
print("Initial observation by worker:")
for i, worker in enumerate(router.workers):
    start = i * ctx_size
    end = start + ctx_size
    worker_obs = obs[start:end]
    print(f"  {worker['worker_id']}: {worker_obs}")


# for step in range(len(jobs)):

#     action = env.action_space.sample()
    
#     obs, reward, done, truncated, info = env.step(action)
    
#     print(f"\nStep {step + 1}")
#     print("Selected worker:", router.workers[action]["worker_id"])
#     print("Reward received:", reward)
#     print("Updated job_cache:", router.workers[action]["job_cache"])
    
#     if done:
#         print("\nAll jobs processed.")
#         break
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=5000)
model.save("worker_selector_model")

print("Training finished and model saved.")

