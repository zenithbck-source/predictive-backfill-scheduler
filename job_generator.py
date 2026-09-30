import random
import pandas as pd

def generate_jobs(n_jobs, seed):
    jobs = []
    random.seed(seed)

    for job in range(n_jobs):
        job_id = (f"J{job:0004d}")
        submit_time = random.randint(0, 10000)
        ncpus = random.choice([1, 2, 4, 8])
        mem = random.choice([1, 2, 4, 8, 16, 32])
        queue_type = random.choice([0, 1, 2])  # 0: short, 1: normal, 2: long
        actual_walltime = ncpus * 2 + mem * 1.5 + (queue_type * 20) + 15
        requested_walltime = int(actual_walltime * random.uniform(0.4, 1.2))

        jobs.append({"job_id":job_id, "submit_time":submit_time, "ncpus":ncpus, "mem_gb":mem, "queue_type":queue_type, "requested_walltime":requested_walltime, "actual_walltime":actual_walltime})

    print(f"{len(jobs)} jobs have been generated.")
    return jobs

if __name__ == "__main__":
    jobs = generate_jobs(2000, 42)