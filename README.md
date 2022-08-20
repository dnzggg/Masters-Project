![GitHub tag (latest SemVer)](https://img.shields.io/github/tag/carla-simulator/scenario_runner.svg)

Formalisation and Verification of Autonomous Vehicles in Simulators
========================
Abstract


Table of Contents
-----------------
- [Signal Temporal Logic Library](#signal-temporal-logic-library)
- [Running the Examples](#running-the-examples)
  - [CARLA Examples](#carla-examples)
  - [Scenic Examples](#scenic-examples)

Signal Temporal Logic Library
-----------------------------
To see how to use the library, please see [STL/README.md](STL/README.md).

Running the Examples
---------------------
### CARLA Examples
To be able to run the examples, you need to have a running CARLA server. To start the server, run the following command:
```bash
./CarlaUE4.sh
```

[CARLA Connection](CARLA%20examples/carla_connection.py) was implemented for testing how the API connects to the server. Also, the map is being changed to Town01 and the available maps are printed out.

[CARLA Weather](CARLA%20examples/carla_weather.py) was implemented for changing the weather conditions using the API.

[CARLA Blueprint](CARLA%20examples/carla_blueprint.py) was implemented for spawning a vehicle and a rgb camera sensor, where the camera saves the images to a folder. The vehicle only records 10 frames after 5 seconds of initialising the world.

[CARLA Replay Scenario](CARLA%20examples/replay_scenario.py) was implemented to replay a scenario and to see what kind of signals can be collected. While replaying a camera is attached to the ego vehicle, and it saves every 20 frames to a folder.


### Scenic Examples
[Running Scenic scenarios](Scenic%20examples/run_scenario.py)