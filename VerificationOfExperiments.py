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

    vel = adv.get_velocity()
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

    # try get_up_vector for longitudinal velocity
    vel = log.get_actor_velocity(ego_id, j)
    velocity = np.array([vel.x, vel.y, vel.z])
    v_h = (ego_rot @ velocity)[0]

    vel = adv.get_velocity()
    velocity = np.array([vel.x, vel.y, vel.z])
    v_p = (adv_rot @ velocity)[0]

    delta_time = log.get_delta_time(j)
    safe_distance = max(0, v_h * delta_time + 0.5 * max_longitudinal_acceleration * (delta_time ** 2)
                        + ((v_h + delta_time * max_longitudinal_acceleration) ** 2) / (2 * min_longitudinal_brake)
                        - (v_p ** 2) / (2 * max_longitudinal_brake))
    return safe_distance

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

    file = os.path.dirname(__file__) + "/records/RouteScenario_0_rep0.log"
    info = client.show_recorder_file_info(file, True)

    log = MetricsLog(info)

    ego_id = log.get_ego_vehicle_id()

    robustness = []
    robustness_1 = []
    robustness_2 = []
    sig = {"x": [], "y": [], "z": [], "t": [], "a": [], "p": []}
    time = []

    start_ego, end_ego = log.get_actor_alive_frames(ego_id)
    start = start_ego
    end = end_ego - 1
    duration = log.get_platform_time(end) - log.get_platform_time(start)
    points = end - start
    time_period = duration

    client.replay_file(file, 0, 0, ego_id, True)

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

        closest_vehicle_in_front = (None, float('inf'))
        closest_vehicle_side = (None, float('inf'))
        waypoint = world.get_map().get_waypoint(ego_vehicle.get_location(), project_to_road=False,
                                                lane_type=carla.LaneType.Driving)
        for a in actor_list:
            if a.id != ego_id:
                waypoint_adv = world.get_map().get_waypoint(a.get_location(), project_to_road=False,
                                                            lane_type=carla.LaneType.Driving)
                try:
                    if waypoint.road_id == waypoint_adv.road_id and waypoint.lane_id == waypoint_adv.lane_id:
                        if waypoint.transform.rotation.yaw < 80:
                            if waypoint.transform.location.x < waypoint_adv.transform.location.x:
                                distance = waypoint_adv.transform.location.distance(waypoint.transform.location)
                                if closest_vehicle_in_front[1] > distance:
                                    closest_vehicle_in_front = a, distance
                        elif 80 <= waypoint.transform.rotation.yaw < 170:
                            if waypoint.transform.location.y < waypoint_adv.transform.location.y:
                                distance = waypoint_adv.transform.location.distance(waypoint.transform.location)
                                if closest_vehicle_in_front[1] > distance:
                                    closest_vehicle_in_front = a, distance
                        elif 170 <= waypoint.transform.rotation.yaw < 260:
                            if waypoint.transform.location.x > waypoint_adv.transform.location.x:
                                distance = waypoint_adv.transform.location.distance(waypoint.transform.location)
                                if closest_vehicle_in_front[1] > distance:
                                    closest_vehicle_in_front = a, distance
                        elif waypoint.transform.rotation.yaw >= 260:
                            if waypoint.transform.location.y > waypoint_adv.transform.location.y:
                                distance = waypoint_adv.transform.location.distance(waypoint.transform.location)
                                if closest_vehicle_in_front[1] > distance:
                                    closest_vehicle_in_front = a, distance
                except AttributeError:
                    pass
                try:
                    if waypoint.road_id == waypoint_adv.road_id and waypoint.lane_id - 1 == waypoint_adv.lane_id:
                        distance = waypoint_adv.transform.location.distance(waypoint.transform.location)
                        if closest_vehicle_side[1] > distance:
                            closest_vehicle_side = a, distance
                except AttributeError:
                    pass
        lane_width = waypoint.lane_width / 2
        if closest_vehicle_side[0] is not None:
            safe_lateral_distance = calculate_minimal_safe_lateral_distance(log, ego_vehicle, closest_vehicle_side[0], j)
            print(safe_lateral_distance + lane_width)
            print(closest_vehicle_side[1])
        if closest_vehicle_in_front[0] is not None:
            print("In front", closest_vehicle_in_front[0].id)
            safe_longitudinal_distance = calculate_minimal_safe_longitudinal_distance(log, ego_vehicle, closest_vehicle_in_front[0], j)
            print(safe_longitudinal_distance)

        world.tick()

    client.stop_replayer(keep_actors=False)
    vehicles = world.get_actors().filter('vehicle.*')
    sensors = world.get_actors().filter('sensors.*')
    for a in vehicles:
        a.destroy()
    for a in sensors:
        a.destroy()
    world.tick()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
