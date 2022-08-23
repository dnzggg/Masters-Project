import os
import subprocess
import time

agents = ["leaderboard/leaderboard/autoagents/basic_agent.py"]
agent_configs = ["leaderboard/leaderboard/autoagents/human_agent_config.txt"]

p = subprocess.Popen(
    ["python", os.environ["LEADERBOARD_ROOT"] + "/leaderboard/leaderboard_evaluator.py", "--scenarios",
     os.environ["SCENARIOS"], "--routes", os.environ["LEADERBOARD_ROOT"] + os.environ["ROUTES"],
     "--repetitions", os.environ["REPETITIONS"], "--agent", agents[0], "--agent-config", agent_configs[0],
     "--debug", "1", "--record", os.path.dirname(__file__) + "/records"], stdout=subprocess.PIPE,
    universal_newlines=True)

while True:
    time.sleep(1)
    print(p.stdout.readline())
    if p.poll() is not None:
        p.kill()
        for output in p.stdout.readlines():
            print(output.strip())
        break
