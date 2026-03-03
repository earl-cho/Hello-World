import subprocess
import time
from datetime import datetime

# 설정
SCRIPTS = [
    "/Users/earl/Blackboard/crawler_v3.py",
    "/Users/earl/Blackboard/crawler_sbi.py",
    "/Users/earl/Blackboard/scalper.py",
    "/Users/earl/Blackboard/article_writer.py",
    "/Users/earl/Blackboard/engine.py"
]
PYTHON_PATH = "/Users/earl/Blackboard/venv/bin/python"

def run_task(script_path):
    print(f"Running {script_path}...")
    try:
        subprocess.run([PYTHON_PATH, script_path], check=True)
        print(f"Successfully finished {script_path}")
    except Exception as e:
        print(f"Error running {script_path}: {e}")

def main():
    print(f"Blackboard Main Automation Started at {datetime.now()}")
    for script in SCRIPTS:
        run_task(script)
    print(f"All tasks finished at {datetime.now()}")

if __name__ == "__main__":
    main()
