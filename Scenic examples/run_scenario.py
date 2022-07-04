import scenic
from scenic.simulators.carla import simulator
import os

scenario = scenic.scenarioFromFile("backgroundActivity.scenic", model="scenic.simulators.carla.model")
sim = simulator.CarlaSimulator(carla_map="Town05", map_path="Town05.xodr", record=os.path.dirname(__file__)+"/records", timeout=60)
for i in range(2):
    scene, _ = scenario.generate()
    simulation = sim.simulate(scene, maxSteps=100)
    if simulation:
        for i, state in enumerate(simulation.trajectory):
            cars = []
            egoPosition, *cars = state
            print(f"Time step {i}: ego position {egoPosition} and other car positions {cars}")
    print(simulation.terminationReason)
sim.destroy()
