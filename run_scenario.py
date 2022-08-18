import os
import subprocess
import time

scenario = "SignalizedJunctionRightTurn_5"

script1 = subprocess.Popen(["python", "scenario_runner/scenario_runner.py",
                            "--scenario", scenario, "--reloadWorld", "--record",
                            os.path.dirname(__file__)+"/records", "--randomize",
                            "--sync"])
# script2 = subprocess.Popen(["python", "scenario_runner/automatic_control.py",
#                             "--scenario", scenario, "-a", "Imitation"])
script2 = subprocess.Popen(["python", "scenario_runner/manual_control.py"])


while True:
    time.sleep(1)
    # print("Waiting for scenario to finish...")d
    if script1.poll() is not None or script2.poll() is not None:
        script1.kill()
        script2.kill()
        # print("Scenario finished!")
        break
    else:
        # print("Scenario still running...")
        pass
