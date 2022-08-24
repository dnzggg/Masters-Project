![GitHub tag (latest SemVer)](https://img.shields.io/badge/keywords-STL%2CCARLA%2CVerification-red)
[![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/carla-simulator/scenario_runner.svg)](https://github.com/carla-simulator/carla/tree/0.9.13)

Formalisation and Verification of Autonomous Vehicles in Simulators
========================
Abstract


Table of Contents
-----------------
- [Signal Temporal Logic Library](#signal-temporal-logic-library)
- [Running the Examples](#running-the-examples)
  - [CARLA Examples](#carla-examples)
  - [Scenic Examples](#scenic-examples)
  - [STL Examples](#stl-examples)
- [ScenarioRunner Examples](#scenariorunner)
- [Leaderboard](#leaderboard)
- [Setting-up Experiments](#setting-up-experiments)
- [Verification](#verification-of-scenarios)

Signal Temporal Logic Library
-----------------------------
To see how to use the library, please see [STL/README.md](STL/README.md).

Also, [playing around with STL](testing_stl_without_library.py) was a good staring point for implementing the STL Library.

Running the Examples
---------------------
Before running the examples some environment variables need to be set.
For linux, use:
```bash
export CARLA_ROOT=/path/to/carla
export ...
```
For windows, use:
```powershell
set CARLA_ROOT=C:\path\to\carla
set ...
```

### CARLA Examples
To be able to run the examples, you need to have a running CARLA server. To start the server, run the following command:
For linux, use:
```bash
./CarlaUE4.sh
```
For windows, use:
```powershell
CarlaUE4.exe
```

[CARLA Connection](CARLA%20examples/carla_connection.py) was implemented for testing how the API connects to the server. Also, the map is being changed to Town01 and the available maps are printed out.

[CARLA Weather](CARLA%20examples/carla_weather.py) was implemented for changing the weather conditions using the API.

[CARLA Blueprint](CARLA%20examples/carla_blueprint.py) was implemented for spawning a vehicle and a rgb camera sensor, where the camera saves the images to a folder. The vehicle only records 10 frames after 5 seconds of initialising the world.

[CARLA Replay Scenario](CARLA%20examples/replay_scenario.py) was implemented to replay a scenario and to see what kind of signals can be collected. While replaying a camera is attached to the ego vehicle, and it saves every 20 frames to a folder.


### Scenic Examples
[Running Scenic scenarios](Scenic%20examples/run_scenario.py) is done by using the Scenic Python API to load a Scenic scenario and run it in the CARLA simulator.
The list of example scenarios can be found in the [Scenic Examples](Scenic%20examples) folder. Some of which are dynamic scenarios and some are static scenarios.
For the scenarios to be generated an OpenDRIVE file is needed. In the example provided the CARLA map Town05 is given.
Scenic Python API works by using the map and the scenario file to generate a scenario. The scenario is then run in the CARLA simulator.


### STL Examples
[STL testing](STL_example.py), [STL with CARLA](STL_CARLA_example.py), [Safe Longitudinal Distance](safe_distance_example.py),


ScenarioRunner
--------------
ScenarioRunner is used in this project to generate and run scenarios. First, Scenic was going to be used, but we thought that it is easier to integrate external agents into ScenarioRunner.
It also contains a number of other functionalities, such as having its own Python API built on top of the CARLA API, and a log reader which is really useful for the case of signal collection.

Check [ScenarioRunner](scenario_runner/README.md) for a more detailed overview. There has been some changes in the code, but nothing that changes the functionality.

To be able to run a scenario in ScenarioRunner with the OpenSCENARIO specification there needs to be a controller that takes control of the ego vehicle.
For this reason a [script](run_scenario.py) has been created where the scenario and the controller are initiated at the same time.

Leaderboard
-----------
Leaderboard uses ScenarioRunner to run an agent passed to it in a route. During the execution of the routes ScenarioRunner creates scenarios according to the NHTSA typology.

Check [Leaderboard](leaderboard/README.md) for a more detailed overview. There has been minor changes in the code, but nothing that changes the functionality.

To run the [Leaderboard evaluator](leaderboard/leaderboard/leaderboard_evaluator.py):
```bash
python run_experiments.py
```

Setting-up Experiments
-------------------
Setting environment variables.

Verification of Scenarios
-------------------------
[Verification](VerificationOfExperiments.py)