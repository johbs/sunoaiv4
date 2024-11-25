from typing import Dict, Optional
import time
import json
import os

# Get tasks directory from environment variable, default to 'tasks' for local development
TASKS_DIR = os.getenv('TASKS_DIR', 'tasks')

def ensure_tasks_dir():
    if not os.path.exists(TASKS_DIR):
        os.makedirs(TASKS_DIR)

def save_task(task_id: str, status: str, result: Optional[Dict] = None):
    ensure_tasks_dir()
    task_data = {
        "status": status,
        "result": result,
        "timestamp": time.time()
    }
    with open(os.path.join(TASKS_DIR, f"{task_id}.json"), "w") as f:
        json.dump(task_data, f)

def get_task(task_id: str) -> Optional[Dict]:
    try:
        with open(os.path.join(TASKS_DIR, f"{task_id}.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
