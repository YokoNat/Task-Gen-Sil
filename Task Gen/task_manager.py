import os
import pandas as pd

class TaskManager:
    def __init__(self, tasks_dir):
        self.tasks_dir = tasks_dir

    def list_tasks(self):
        # List all CSV files in the tasks directory
        return [f for f in os.listdir(self.tasks_dir) if f.lower().endswith('.csv')]

    def load_task(self, filename):
        # Load a CSV file as a pandas DataFrame
        path = os.path.join(self.tasks_dir, filename)
        print(f"Attempting to load file at: {os.path.abspath(path)}")  # Debug log
        print(f"File exists: {os.path.exists(path)}")  # Debug log
        return pd.read_csv(path)

    def save_task(self, filename, df):
        # Save a pandas DataFrame to a CSV file
        path = os.path.join(self.tasks_dir, filename)
        df.to_csv(path, index=False)

if __name__ == "__main__":
    # Minimal test: list tasks and load the first one
    tasks_dir = os.path.join(os.path.dirname(__file__), '../shhh/tasks/TASKS')
    manager = TaskManager(tasks_dir)
    tasks = manager.list_tasks()
    print("Tasks:", tasks)
    if tasks:
        df = manager.load_task(tasks[0])
        print(f"Loaded {tasks[0]}:")
        print(df.head()) 