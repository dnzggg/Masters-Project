import scenic
from scenic.simulators.carla import simulator
import os

scenario = scenic.scenarioFromFile("dynamic_example.scenic", model="scenic.simulators.carla.model")
print()
sim = simulator.CarlaSimulator(carla_map=None, map_path=os.path.abspath("Town05.xodr"),
                               record=os.path.dirname(__file__)+"/records", timeout=60)
for i in range(2):
    scene, _ = scenario.generate()
    simulation = sim.simulate(scene, maxSteps=1000)
    if simulation:
        for i, state in enumerate(simulation.trajectory):
            cars = []
            egoPosition, *cars = state
            print(f"Time step {i}: ego position {egoPosition} and other car positions {cars}")
    # print(simulation.terminationReason)
sim.destroy()
