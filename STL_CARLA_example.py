import glob
import os
import re
import sys
import matplotlib.pyplot as plt

import STL

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def distance(v1, v2):
    return v1.distance(v2)


def main():
    # Client creation
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()

    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    file = "C:/Users/Deniz Gorur/PycharmProjects/Masters Project/Scenic examples/records/scenario1.log"
    info = client.show_recorder_file_info(file, True)
    frames = int(re.search(r"Frames: (\d+)", info).group(1))
    duration = float(re.search(r"Duration: (\d+)\.(\d+)", info).group(1))
    client.replay_file(file, 0, 0, 2028)

    world.tick()

    actor_list = world.get_actors()
    vehicle = list(actor_list.filter('vehicle.tesla.model3'))[0]
    vehicle2 = list(actor_list.filter('vehicle.toyota.prius'))[0]

    x = STL.parse('(x<20)')
    y = STL.parse('<->[0,1] y')
    phi = y

    robustness = []
    b_robustness = []
    sig = {"x": [], "y": []}
    time = []
    points = frames * 2
    time_period = duration

    for i in range(frames * 2):
        world.tick()
        dist = vehicle.get_location().distance(vehicle2.get_location())
        sig["x"].append(dist)
        sig["y"].append(vehicle.is_at_traffic_light())
        time.append(i * 0.05)
        val = STL.evaluate(phi, sig, time, t=i, points=points, time_period=time_period)
        val = 1 if val == float('inf') else val
        val = 0 if val == float('-inf') else val
        robustness.append(val)
        b_robustness.append(1 if val >= 0 else 0)

    vehicles = world.get_actors().filter('vehicle.*')
    sensors = world.get_actors().filter('sensors.*')
    for a in vehicles:
        a.destroy()
    for a in sensors:
        a.destroy()

    plt.plot(time, sig["y"], time, robustness, "r--")
    plt.show()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
