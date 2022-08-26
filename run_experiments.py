import os
import subprocess
import time

agents = ["leaderboard/leaderboard/autoagents/basic_agent.py", "leaderboard/leaderboard/autoagents/behaviour_agent.py"]
agent_configs = ["", ""]

for i in range(0, len(agents)):
    for route in range(4, 5):
        p = subprocess.Popen(
            ["python", os.environ["LEADERBOARD_ROOT"] + "/leaderboard/leaderboard_evaluator.py", "--scenarios",
             os.environ["SCENARIOS"], "--routes", os.environ["LEADERBOARD_ROOT"] + os.environ["ROUTES"],
             "--repetitions", "3", "--agent", agents[i], "--agent-config", agent_configs[i],
             "--checkpoint", os.environ["CHECKPOINT_ENDPOINT"], "--route-id", str(route),
             "--debug", "0", "--record", os.path.dirname(__file__) + "/records"])

        while True:
            time.sleep(0.1)
            if p.poll() is not None:
                p.kill()
                break
        p.kill()
        time.sleep(1)

