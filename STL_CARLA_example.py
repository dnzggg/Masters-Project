import glob
import os
import re
import sys
import matplotlib.pyplot as plt
from scenario_runner.srunner.metrics.tools.metrics_log import MetricsLog

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

    file = "C:/Users/Deniz Gorur/PycharmProjects/Masters Project/records/FollowLeadingVehicle_1.log"
    info = client.show_recorder_file_info(file, True)

    log = MetricsLog(info)

    frames = log.get_total_frame_count()
    duration = log.get_delta_time(frames - 1)

    ego_id = log.get_ego_vehicle_id()
    adv_id = log.get_actor_ids_with_role_name("scenario")[0]

    client.replay_file(file, 0, 0, ego_id)
    world.tick()

    actor_list = world.get_actors()
    vehicle = actor_list.find(ego_id)
    vehicle2 = actor_list.find(adv_id)

    x = STL.parse('(x<20)')
    y = STL.parse('<->[0,1] y')
    phi = x.once(lo=0, hi=5)

    robustness = []
    b_robustness = []
    sig = {"x": [], "y": []}
    time = []
    points = frames * 2
    time_period = duration

    for i in range(frames * 2):
        world.tick()
        if vehicle.get_location() == carla.Location(0, 0, 0) or vehicle2.get_location() == carla.Location(0, 0, 0):
            break
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

    plt.plot(time, sig["x"], time, robustness, "r--")
    plt.show()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
