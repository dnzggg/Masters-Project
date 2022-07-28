import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np

import STL
from scenario_runner.srunner.metrics.tools.metrics_log import MetricsLog

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla


def main():
    # Client creation
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    file = os.path.dirname(__file__) + "/records/FollowLeadingVehicle_2.log"
    info = client.show_recorder_file_info(file, True)

    log = MetricsLog(info)

    ego_id = log.get_ego_vehicle_id()
    adv_id = log.get_actor_ids_with_role_name("scenario")[0]

    x = STL.parse('(x<0)')  # x is the distance - safe distance
    y = STL.parse('(y<1.5)')  # y is the relative difference between velocities
    z = STL.parse('(z<25)')  # z is the distance
    t = STL.parse('t')  # t is when the ego vehicle is decelerating due to traffic light

    time_headway = 1.5
    vehicle_mass = 1200
    g = -0.25 * (time_headway + 1) / vehicle_mass

    a = STL.parse(f'(a<{g})')  # a is the acceleration of the ego vehicle
    p = STL.parse(f'(p<{g})')  # p is the acceleration of the adversary vehicle
    phi = x
    phi2 = ~y | z | t
    phi3 = ~a | p.historically(lo=0, hi=3)

    robustness = []
    robustness_1 = []
    robustness_2 = []
    sig = {"x": [], "y": [], "z": [], "t": [], "a": [], "p": []}
    time = []

    start_ego, end_ego = log.get_actor_alive_frames(ego_id)
    start_adv, end_adv = log.get_actor_alive_frames(adv_id)
    start = max(start_ego, start_adv) - 1
    end = min(end_ego, end_adv) - 1
    duration = log.get_platform_time(end) - log.get_platform_time(start)
    points = end - start
    time_period = duration

    # Values used from "Runtime Verification of Autonomous Driving Systems in CARLA"
    max_acceleration = 5.4
    min_brake = 2.9
    max_brake = 9.8

    client.replay_file(file, 0, 0, ego_id)

    for i in range(start):
        world.tick()

    actor_list = world.get_actors()
    vehicle = actor_list.find(ego_id)
    vehicle2 = actor_list.find(adv_id)

    for i in range(points):
        j = i + start

        ego_trans = np.array(log.get_actor_transform(ego_id, j).get_matrix())
        ego_rot = ego_trans[0:3, 0:3].T
        adv_trans = np.array(log.get_actor_transform(adv_id, j).get_matrix())
        adv_rot = adv_trans[0:3, 0:3].T

        # try get_up_vector for longitudinal velocity
        vel = log.get_actor_velocity(ego_id, j)
        velocity = np.array([vel.x, vel.y, vel.z])
        v_h = (ego_rot @ velocity)[0]

        vel = log.get_actor_velocity(adv_id, j)
        velocity = np.array([vel.x, vel.y, vel.z])
        v_p = (adv_rot @ velocity)[0]

        delta_time = log.get_delta_time(j)
        safe_distance = max(0, v_h * delta_time + 0.5 * max_acceleration * delta_time ** 2
                            + ((v_h + delta_time * max_acceleration) ** 2) / (2 * min_brake)
                            - (v_p ** 2) / (2 * max_brake))

        ego_location = log.get_actor_transform(ego_id, j).location
        adv_location = log.get_actor_transform(adv_id, j).location
        dist = abs(ego_location.x - adv_location.x)

        acc_ego = log.get_actor_acceleration_variation(ego_id, j)
        acc_ego = np.array([acc_ego.x, acc_ego.y, acc_ego.z])
        a_e = (ego_rot @ acc_ego)[0]

        acc_adv = log.get_actor_acceleration_variation(adv_id, j)
        acc_adv = np.array([acc_adv.x, acc_adv.y, acc_adv.z])
        a_a = (adv_rot @ acc_adv)[0]

        sig["x"].append(dist - safe_distance)
        sig["y"].append(v_p - v_h)
        sig["z"].append(ego_location.distance(adv_location))
        sig["t"].append(vehicle.is_at_traffic_light())
        sig["a"].append(a_e)
        sig["p"].append(a_a)

        time.append(log.get_platform_time(j))

        val = STL.evaluate(phi, sig, time, t=i, points=points, time_period=time_period)
        val = 1 if val == float('inf') else val
        val = 0 if val == float('-inf') else val
        robustness.append(val)
        val = STL.evaluate(phi2, sig, time, t=i, points=points, time_period=time_period)
        val = 1 if val == float('inf') else val
        val = 0 if val == float('-inf') else val
        robustness_1.append(val)
        val = STL.evaluate(phi3, sig, time, t=i, points=points, time_period=time_period)
        val = 1 if val == float('inf') else val
        val = 0 if val == float('-inf') else val
        robustness_2.append(val)
        world.tick()

    plt.plot(time, sig["x"], time, robustness, "r--")
    plt.show()
    plt.plot(time, sig["y"], time, sig["z"], time, np.array(sig["t"]) * 5, time, robustness_1, "r--")
    plt.show()
    plt.plot(time, sig["a"], time, sig["p"], time, robustness_2, "r--")
    plt.show()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
