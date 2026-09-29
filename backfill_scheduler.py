import pandas as pd
from job_generator import generate_jobs


def run_backfill_scheduler(jobs, total_cores, runtime_column):
    # Sort jobs by submission time.
    jobs = sorted(jobs, key=lambda job: job['submit_time'])

    total_jobs = len(jobs)
    avail_cores = total_cores
    queue_id = 1
    time = 0

    schedule = []
    queue = []
    running = []

    # Continue until all jobs have been processed.
    while len(schedule) < total_jobs:

        # ---------------------------------------------------------
        # 1. Move completed jobs out of running
        # ---------------------------------------------------------
        completed_jobs = [
            job for job in running
            if job['end_time'] <= time
        ]

        for job in completed_jobs:
            avail_cores += job['ncpus']
            job['state'] = 'E'
            schedule.append(job)

        # Remove completed jobs from running.
        running = [
            job for job in running
            if job['end_time'] > time
        ]

        # ---------------------------------------------------------
        # 2. Move newly-arrived jobs into the queue
        # ---------------------------------------------------------
        arrived_jobs = [
            job for job in jobs
            if job['submit_time'] <= time
        ]

        for job in arrived_jobs:
            job['state'] = 'Q'
            queue.append(job)

        # Remove arrived jobs from jobs.
        jobs = [
            job for job in jobs
            if job['submit_time'] > time
        ]

        # Keep queue in FIFO order.
        queue.sort(key=lambda job: job['submit_time'])

        # ---------------------------------------------------------
        # 3. Try to schedule jobs
        # ---------------------------------------------------------
        progressed = True

        while progressed:
            progressed = False

            if not queue:
                break

            # -----------------------------------------------------
            # 3A. Try the head job first
            # -----------------------------------------------------
            head_job = queue[0]

            if head_job['ncpus'] <= avail_cores:

                head_job['state'] = 'S'
                head_job['queue'] = queue_id
                head_job['start_time'] = time
                head_job['end_time'] = (
                    time + head_job[runtime_column]
                )

                avail_cores -= head_job['ncpus']
                queue_id += 1

                running.append(head_job)
                queue.pop(0)

                progressed = True

                continue

            # -----------------------------------------------------
            # 3B. Head job cannot run.
            #
            # Find the earliest time at which enough resources
            # will become available for the head job.
            # -----------------------------------------------------
            future_cores = avail_cores
            head_job_start = None

            # Running jobs must be considered in completion order.
            completion_order = sorted(
                running,
                key=lambda job: job['end_time']
            )

            for running_job in completion_order:
                future_cores += running_job['ncpus']

                if future_cores >= head_job['ncpus']:
                    head_job_start = running_job['end_time']
                    break

            # If there is no way to free enough cores, stop.
            if head_job_start is None:
                break

            # -----------------------------------------------------
            # 3C. Backfill a later job.
            #
            # A later job may run if:
            #
            #   1. It fits in the currently available cores.
            #   2. It finishes before the head job's reservation.
            # -----------------------------------------------------
            backfilled = False

            for candidate in queue[1:]:

                candidate_runtime = candidate[runtime_column]
                candidate_end = time + candidate_runtime

                if (
                    candidate['ncpus'] <= avail_cores
                    and candidate_end <= head_job_start
                ):
                    candidate['state'] = 'S'
                    candidate['queue'] = queue_id
                    candidate['start_time'] = time
                    candidate['end_time'] = candidate_end

                    avail_cores -= candidate['ncpus']
                    queue_id += 1

                    running.append(candidate)
                    queue.remove(candidate)

                    backfilled = True
                    progressed = True

                    # Re-evaluate the queue after every backfill.
                    break

            # If no job could be backfilled, stop trying at this time.
            if not backfilled:
                break

        # ---------------------------------------------------------
        # 4. Advance simulated time
        # ---------------------------------------------------------
        time += 1

    # -------------------------------------------------------------
    # 5. Print any jobs that were not completed
    # -------------------------------------------------------------
    print(f"Still in jobs: {[j['job_id'] for j in jobs]}")
    print(f"Still in queue: {[j['job_id'] for j in queue]}")
    print(f"Still in running: {[j['job_id'] for j in running]}")

    return schedule


if __name__ == "__main__":
    jobs = generate_jobs(100, 42)

    output = run_backfill_scheduler(
        jobs,
        total_cores=32,
        runtime_column='actual_walltime'
    )

    for job in output:
        print(job)
