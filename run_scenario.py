import subprocess
import time
import os


script1 = subprocess.Popen(["python", "scenario_runner/scenario_runner.py", "--scenario", "FollowLeadingVehicle_1", "--reloadWorld", "--record", os.path.dirname(__file__)+"/records"])
script2 = subprocess.Popen(["python", "scenario_runner/manual_control.py"])

while True:
    time.sleep(1)
    print("Waiting for scenario to finish...")
    if script1.poll() is not None:
        print("Scenario finished!")
        break
    else:
        print("Scenario still running...")
