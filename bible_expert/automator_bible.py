import subprocess
import os
from datetime import datetime

# 경로 설정
PYTHON_PATH = "/Users/earl/Blackboard/venv/bin/python"
SCRIPT_PATH = "/Users/earl/Blackboard/bible_expert/bible_writer.py"
LOG_PATH = "/Users/earl/Blackboard/bible_expert/automation.log"

def run_automation():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- Automation Rule Started at {now} ---")
    
    try:
        result = subprocess.run(
            [PYTHON_PATH, SCRIPT_PATH],
            capture_output=True,
            text=True,
            check=True
        )
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"[{now}] SUCCESS\n")
            log.write(result.stdout + "\n")
            
    except subprocess.CalledProcessError as e:
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"[{now}] FAILED\n")
            log.write(e.stderr + "\n")
            
    print(f"--- Automation Rule Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

if __name__ == "__main__":
    run_automation()
