import os
import subprocess
import time

agents = ["leaderboard/leaderboard/autoagents/basic_agent.py", "leaderboard/leaderboard/autoagents/behaviour_agent.py",
          os.environ["TRANSFUSER_PATH"] + "/team_code_transfuser/submission_agent.py"]
agent_configs = ["", "", os.environ["TRANSFUSER_PATH"] + "/model_ckpt/transfuser"]
agent_names = ["basic_agent", "behaviour_agent", "transfuser"]

for i in range(0, len(agents)):
    for route in range(0, 8):
        p = subprocess.Popen(
            ["python", os.environ["LEADERBOARD_ROOT"] + "/leaderboard/leaderboard_evaluator.py", "--scenarios",
             os.environ["LEADERBAORD_ROOT"] + "/data/all_towns_traffic_scenarios_public.json", "--routes", os.environ["LEADERBOARD_ROOT"] + os.environ["ROUTES"],
             "--repetitions", "3", "--agent", agents[i], "--agent-config", agent_configs[i],
             "--checkpoint", f"s{route}_{agent_names[i]}.json", "--route-id", str(route),
             "--debug", "0", "--record", os.path.dirname(__file__) + "/records", "--resume", "1"])

        while True:
            time.sleep(0.5)
            if p.poll() is not None:
                p.kill()
                break
        p.kill()

