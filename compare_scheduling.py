import pandas as pd
import copy
from job_generator import generate_jobs
from predict_runtimes import add_predicted_runtimes
from backfill_scheduler import run_backfill_scheduler


jobs = generate_jobs(100, 30)
jobs = add_predicted_runtimes(jobs)

req_jobs = run_backfill_scheduler(
    copy.deepcopy(jobs),
    total_cores=16,
    runtime_column='requested_walltime'
    )
act_jobs = run_backfill_scheduler(
    copy.deepcopy(jobs),
    total_cores=16,
    runtime_column='actual_walltime'
    )
pred_jobs = run_backfill_scheduler(
    copy.deepcopy(jobs),
    total_cores=16,
    runtime_column='predicted_walltime'
    )

req_jobs = pd.DataFrame(req_jobs)
act_jobs = pd.DataFrame(act_jobs)
pred_jobs = pd.DataFrame(pred_jobs)

req_jobs['wait_time'] = req_jobs['start_time'] - req_jobs['submit_time']
act_jobs['wait_time'] = act_jobs['start_time'] - act_jobs['submit_time']
pred_jobs['wait_time'] = pred_jobs['start_time'] - pred_jobs['submit_time']

req_avg_wait = req_jobs['wait_time'].mean()
act_avg_wait = act_jobs['wait_time'].mean()
pred_avg_wait = pred_jobs['wait_time'].mean()

print("=== Average Wait Time ===")
print(f"Requested: {req_avg_wait}")
print(f"Actual:    {act_avg_wait}")
print(f"Predicted: {pred_avg_wait}")

print("\n\n=== Preview of Jobs ===")
print(f"\nRequested:\n{req_jobs.sort_values('job_id').sample(5, random_state=42)}")
print(f"\nActual:\n{act_jobs.sort_values('job_id').sample(5, random_state=42)}")
print(f"\nPredicted:\n{pred_jobs.sort_values('job_id').sample(5, random_state=42)}")