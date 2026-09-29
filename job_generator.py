import random
import pandas as pd

def generate_jobs(n_jobs, seed):
    jobs = []
    random.seed(seed)

    for job in range(n_jobs):
        job_id = (f"J{job:0004d}")
        submit_time = random.randint(0, 10000)
        ncpus = random.choice([1, 2, 4, 8])
        requested_walltime = random.randint(5, 500)
        actual_walltime = int(requested_walltime * random.uniform(0.4, 1.2))

        jobs.append({"job_id":job_id, "submit_time":submit_time, "ncpus":ncpus, "requested_walltime":requested_walltime, "actual_walltime":actual_walltime})

    print(f"{len(jobs)} jobs have been generated.")
    return jobs

if __name__ == "__main__":
    jobs = generate_jobs(2000, 42)