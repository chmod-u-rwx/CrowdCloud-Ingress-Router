import random
import string
import pandas as pd

# Possible HTTP methods
METHODS = ["GET", "POST", "PUT", "DELETE"]

# Generate random string
def random_string(length=6):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

# Generate job dataset
def generate_jobs(n=100):
    jobs = []
    for i in range(1, n+1):
        job = {
            "job_id": f"job_{i}",
            "repo_link": f"https://github.com/example/repo{i}",
            "path": f"/api/{random_string(5)}",
            "method": random.choice(METHODS),
            "query_params": {"param": random.randint(1, 100)},
            "body": {"data": random_string(8)},
            "headers": {"Authorization": f"Bearer token{i}"},
        }
        jobs.append(job)
    return jobs

# Create dataset
jobs = generate_jobs(100)

# Convert to DataFrame
df = pd.DataFrame(jobs)

# Save to Excel
df.to_excel("jobs_dataset.xlsx", index=False)

print("✅ jobs_dataset.xlsx generated successfully with method column!")
