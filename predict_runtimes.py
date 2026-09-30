import torch
import torch.nn as nn
from job_generator import generate_jobs

class RuntimePredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(3, 128)
        self.layer2 = nn.Linear(128, 64)
        self.layer3 = nn.Linear(64, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.layer3(x)
        return x

def add_predicted_runtimes(jobs):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = RuntimePredictor().to(device)
    model.load_state_dict(torch.load("runtime_model.pth", map_location=device))
    model.eval()

    # build a list of [ncpus, mem_gb, submit_hour, queue_type] per job
    X = [[job['ncpus'], job['mem_gb'], job['queue_type']] for job in jobs]
    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)

    with torch.no_grad():
        predictions = model(X_tensor).cpu().numpy().flatten()

    # attach the prediction back onto each job dictionary
    for job, pred in zip(jobs, predictions):
        job['predicted_runtime'] = float(pred)

    return jobs

if __name__ == "__main__":
    jobs = generate_jobs(500, 7)
    jobs = add_predicted_runtimes(jobs)
    for job in jobs:
        print(job)