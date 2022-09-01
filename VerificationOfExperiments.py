import glob
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from srunner.metrics.tools.metrics_log import MetricsLog

import STL

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import json

max_longitudinal_acceleration = 3.5
min_longitudinal_brake = 4.0
max_longitudinal_brake = 8.0
max_lateral_acceleration = 0.2
min_lateral_brake = 0.8


def get_rotation_matrix(log, ego_id, adv, j):
    ego_trans = np.array(log.get_actor_transform(ego_id, j).get_matrix())
    ego_rot = ego_trans[0:3, 0:3].T

    adv_trans = np.array(adv.get_transform().get_matrix())
    adv_rot = adv_trans[0:3, 0:3].T

    return ego_rot, adv_rot


def calculate_minimal_safe_lateral_distance(log, ego, adv, j):
    ego_id = ego.id
    ego_rot, adv_rot = get_rotation_matrix(log, ego_id, adv, j)

    vel = log.get_actor_velocity(ego_id, j)
    velocity = np.array([vel.x, vel.y, vel.z])
    v_1 = (ego_rot @ velocity)[1]

    vel = log.get_actor_velocity(adv.id, j)
    velocity = np.array([vel.x, vel.y, vel.z])
    v_2 = (adv_rot @ velocity)[1]

    delta_time = log.get_delta_time(j)

    v_1_p = v_1 + 0.05 * max_lateral_acceleration
    v_2_p = v_2 + 0.05 * max_lateral_acceleration

    safe_lateral_distance = max(0, ((v_1 + v_1_p) / 2) * delta_time + (v_1_p ** 2) / (2 * min_lateral_brake) -
                                (((v_2 + v_2_p) / 2) * delta_time - (v_2_p ** 2) / (2 * min_lateral_brake)))
    return safe_lateral_distance


def calculate_minimal_safe_longitudinal_distance(log, ego, adv, j):
    ego_id = ego.id
    ego_rot, adv_rot = get_rotation_matrix(log, ego_id, adv, j)

    vel = log.get_actor_velocity(ego_id, j)
    velocity = np.array([vel.x, vel.y, vel.z])
    v_h = (ego_rot @ velocity)[0]

    accel = log.get_actor_acceleration_variation(ego_id, j)
    acceleration = np.array([accel.x, accel.y, accel.z])
    a_h = (ego_rot @ acceleration)[0]

    vel = log.get_actor_velocity(adv.id, j)
    velocity = np.array([vel.x, vel.y, vel.z])
    v_p = (adv_rot @ velocity)[0]

    accel = log.get_actor_acceleration_variation(adv.id, j)
    acceleration = np.array([accel.x, accel.y, accel.z])
    a_p = (adv_rot @ acceleration)[0]

    delta_time = log.get_delta_time(j)
    safe_distance = max(0, v_h * delta_time + 0.5 * max_longitudinal_acceleration * (delta_time ** 2)
                        + ((v_h + delta_time * max_longitudinal_acceleration) ** 2) / (2 * min_longitudinal_brake)
                        - (v_p ** 2) / (2 * max_longitudinal_brake))

    return safe_distance, v_p, v_h, a_p, a_h


# Works with only two vehicles
def main():
    # Client creation
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    os.chdir('records')
    for file in sorted(glob.glob("*.log")):
        print(file.strip('.log'))
        if len(glob.glob(file.strip('.log') + '.json')) != 0:
            continue
        file = os.path.dirname(__file__) + "/records/" + file
        info = client.show_recorder_file_info(file, True)

        log = MetricsLog(info)

        ego_id = log.get_ego_vehicle_id()

        x = STL.parse('(x<0)')  # x is the longitudinal distance - safe longitudinal distance
        u = STL.parse('(u<0.9)')  # u is the lateral distance - safe lateral distance
        y = STL.parse('(y<1.5)')  # y is the relative difference between velocities
        z = STL.parse('(z<25)')  # z is the distance
        t = STL.parse('t')  # t is if the ego vehicle is decelerating due to traffic light

        time_headway = 1.5
        vehicle_mass = 1200
        g = -0.25 * (time_headway + 1) / vehicle_mass

        a = STL.parse(f'(a<{g})')  # a is the acceleration of the ego vehicle
        p = STL.parse(f'(p<{g})')  # p is the acceleration of the adversary vehicle
        phi_lon = x
        phi_lat = u
        phi2 = ~y | z | t
        phi3 = ~a | p.historically(lo=0, hi=3)

        robustness_lon = []
        robustness_lat = []
        robustness_1 = []
        robustness_2 = []
        sig = {"x": [], "u": [], "y": [], "z": [], "t": [], "a": [], "p": []}
        time = []

        start_ego, end_ego = log.get_actor_alive_frames(ego_id)
        start = start_ego
        end = end_ego - 1
        duration = log.get_platform_time(end) - log.get_platform_time(start)
        points = end - start
        time_period = duration

        client.replay_file(file, 0, 0, ego_id, False)

        for i in range(start):
            world.tick()

        actor_list = world.get_actors()
        ego_vehicle = actor_list.find(ego_id)

        scenario_vehicle_ids = log.get_actor_ids_with_role_name("scenario")

        for i in range(points):
            j = i + start
            actor_list = world.get_actors().filter("*vehicle*")

            for vehicle_id in scenario_vehicle_ids:
                if transform := log.get_actor_transform(vehicle_id, j):
                    if transform.location.distance(ego_vehicle.get_location()) < 15:
                        print("Scenario", vehicle_id)

            time.append(log.get_platform_time(j))

            closest_vehicle_in_front = (None, float('inf'))
            closest_vehicle_side = (None, float('inf'))
            waypoint = world.get_map().get_waypoint(ego_vehicle.get_location(), project_to_road=False,
                                                    lane_type=carla.LaneType.Driving | carla.LaneType.Shoulder)
            transform_ego = ego_vehicle.get_transform()

            for a in actor_list:
                if a.id != ego_id:
                    waypoint_adv = world.get_map().get_waypoint(a.get_location(), project_to_road=False,
                                                                lane_type=carla.LaneType.Driving)
                    transform_adv = a.get_transform()
                    distance = transform_ego.location.distance(transform_adv.location)
                    if (rot := transform_ego.rotation.yaw) < 0:
                        rot = 360 + transform_ego.rotation.yaw

                    try:
                        if waypoint.road_id == waypoint_adv.road_id and waypoint.lane_id == waypoint_adv.lane_id:
                            if rot < 70 or rot >= 340:
                                if transform_ego.location.x < transform_adv.location.x:
                                    if closest_vehicle_in_front[1] > distance:
                                        closest_vehicle_in_front = a, distance
                            elif 70 <= rot < 160:
                                if transform_ego.location.y < transform_adv.location.y:
                                    if closest_vehicle_in_front[1] > distance:
                                        closest_vehicle_in_front = a, distance
                            elif 160 <= rot < 250:
                                if transform_ego.location.x > transform_adv.location.x:
                                    if closest_vehicle_in_front[1] > distance:
                                        closest_vehicle_in_front = a, distance
                            elif 250 <= rot < 340:
                                if transform_ego.location.y > transform_adv.location.y:
                                    if closest_vehicle_in_front[1] > distance:
                                        closest_vehicle_in_front = a, distance
                    except AttributeError:
                        pass

                    distance_y = abs(transform_adv.location.y - transform_ego.location.y)
                    distance_x = abs(transform_adv.location.x - transform_ego.location.x)
                    try:
                        if abs(waypoint.lane_id) == 1:
                            move = int(waypoint.lane_id / abs(waypoint.lane_id))
                        elif abs(waypoint.lane_id) == 2:
                            move = int(-waypoint.lane_id / abs(waypoint.lane_id))

                        if waypoint.road_id == waypoint_adv.road_id and waypoint.lane_id + move == waypoint_adv.lane_id:
                            if rot < 70 or rot >= 340:
                                if closest_vehicle_side[1] > distance_y:
                                    closest_vehicle_side = a, distance_y
                            elif 70 <= rot < 160:
                                if closest_vehicle_side[1] > distance_x:
                                    closest_vehicle_side = a, distance_x
                            elif 160 <= rot < 250:
                                if closest_vehicle_side[1] > distance_y:
                                    closest_vehicle_side = a, distance_y
                            elif 250 <= rot < 340:
                                if closest_vehicle_side[1] > distance_x:
                                    closest_vehicle_side = a, distance_x
                    except AttributeError:
                        pass
            try:
                lane_width = waypoint.lane_width / 2
                if closest_vehicle_side[0] is not None:
                    safe_lateral_distance = calculate_minimal_safe_lateral_distance(log, ego_vehicle,
                                                                                    closest_vehicle_side[0], j)
                    sd_lat = safe_lateral_distance + lane_width
                    sig["u"].append(closest_vehicle_side[1] - sd_lat)
                else:
                    sig["u"].append(0.9)
            except AttributeError:
                sig["u"].append(0.9)
            if closest_vehicle_in_front[0] is not None:
                safe_longitudinal_distance, v_p, v_h, a_p, a_h = calculate_minimal_safe_longitudinal_distance(log,
                                                                    ego_vehicle, closest_vehicle_in_front[0], j)
                sig["x"].append(closest_vehicle_in_front[1] - safe_longitudinal_distance)

                sig["y"].append(v_p - v_h)
                sig["z"].append(ego_vehicle.get_location().distance(closest_vehicle_in_front[0].get_location()))
                sig["t"].append(ego_vehicle.is_at_traffic_light())
                sig["a"].append(a_p)
                sig["p"].append(a_h)
            else:
                sig["x"].append(0)
                sig["y"].append(1.5)
                sig["z"].append(25)
                sig["t"].append(0)
                sig["a"].append(0)
                sig["p"].append(0)

            val = STL.evaluate(phi_lon, sig, time, t=i, points=points, time_period=time_period)
            val = 1 if val == float('inf') else val
            val = 0 if val == float('-inf') else val
            robustness_lon.append(val)
            val = STL.evaluate(phi_lat, sig, time, t=i, points=points, time_period=time_period)
            val = 1 if val == float('inf') else val
            val = 0 if val == float('-inf') else val
            robustness_lat.append(val)
            val = STL.evaluate(phi2, sig, time, t=i, points=points, time_period=time_period)
            val = 1 if val == float('inf') else val
            val = 0 if val == float('-inf') else val
            robustness_1.append(val)
            val = STL.evaluate(phi3, sig, time, t=i, points=points, time_period=time_period)
            val = 1 if val == float('inf') else val
            val = 0 if val == float('-inf') else val
            robustness_2.append(val)
            world.tick()

        client.stop_replayer(keep_actors=False)
        vehicles = world.get_actors().filter('vehicle.*')
        sensors = world.get_actors().filter('sensors.*')
        for a in vehicles:
            a.destroy()
        for a in sensors:
            a.destroy()
        world.tick()

        with open(file.strip('.log') + ".json", 'w', encoding='utf-8') as f:
            json.dump({"robustness_lon": {"sig": robustness_lon, "max": max(robustness_lon), "min": min(robustness_lon), "avg": sum(robustness_lon) / len(robustness_lon)},
                       "robustness_lat": {"sig": robustness_lat, "max": max(robustness_lat), "min": min(robustness_lat), "avg": sum(robustness_lat) / len(robustness_lat)},
                       "robustness_1": {"sig": robustness_1, "max": max(robustness_1), "min": min(robustness_1), "avg": sum(robustness_1) / len(robustness_1)},
                       "robustness_2": {"sig": robustness_2, "max": max(robustness_2), "min": min(robustness_2), "avg": sum(robustness_2) / len(robustness_2)}},
                      f, indent=4)

        # plt.plot(time, sig["x"], time, robustness_lon, "r--")
        # plt.show()
        # plt.plot(time, sig["u"], time, robustness_lat, "r--")
        # plt.show()
        # plt.plot(time, sig["y"], time, sig["z"], time, np.array(sig["t"]) * 5, time, robustness_1, "r--")
        # plt.show()
        # plt.plot(time, sig["a"], time, sig["p"], time, robustness_2, "r--")
        # plt.show()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
