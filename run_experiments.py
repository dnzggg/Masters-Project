import os
import subprocess
import time

agents = ["leaderboard/leaderboard/autoagents/basic_agent.py", "leaderboard/leaderboard/autoagents/behaviour_agent.py"]
agent_configs = ["", ""]

for route in range(2):
    for i in range(len(agents)):
        p = subprocess.Popen(
            ["python", os.environ["LEADERBOARD_ROOT"] + "/leaderboard/leaderboard_evaluator.py", "--scenarios",
             os.environ["SCENARIOS"], "--routes", os.environ["LEADERBOARD_ROOT"] + os.environ["ROUTES"],
             "--repetitions", "1", "--agent", agents[i], "--agent-config", agent_configs[i],
             "--checkpoint", os.environ["CHECKPOINT_ENDPOINT"], "--route-id", str(route),
             "--debug", "0", "--record", os.path.dirname(__file__) + "/records"], stdout=subprocess.PIPE,
            universal_newlines=True)

        while True:
            time.sleep(1)
            print(p.stdout.readline())
            if p.poll() is not None:
                p.kill()
                for output in p.stdout.readlines():
                    print(output.strip())
                break
        p.kill()
        time.sleep(1.5)
