import os
import subprocess
import time

scenario = "SignalizedJunctionRightTurn_5"

script1 = subprocess.Popen(["python", "--randomize","--sync"
                            "scenario_runner/scenario_runner.py",
                            "--reloadWorld", "--record",
                            os.path.dirname(__file__) + "/records",
                            "--scenario", scenario])
script2 = subprocess.Popen(["python",
                            "scenario_runner/manual_control.py"])


while True:
    time.sleep(1)
    if script1.poll() is not None or script2.poll() is not None:
        script1.kill()
        script2.kill()
        break
