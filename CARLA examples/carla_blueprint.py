import queue
import sys, os, glob, time

import numpy as np

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from carla import VehicleLightState as vls


def main():
    # Client creation
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    # World connection
    world = client.get_world()

    # Get blueprint library
    blueprint_library = world.get_blueprint_library()
    # Print all blueprints of type 'vehicle.tesla.*'
    teslas = blueprint_library.filter('vehicle.tesla.*')
    print(teslas)
    # Print a specific blueprint
    rgb_camera_sensor = blueprint_library.find('sensor.camera.rgb')
    print(rgb_camera_sensor)

    # Change color of a tesla
    tesla_blueprint = teslas[1]
    tesla_blueprint.set_attribute('color', '255,255,255')
    print(tesla_blueprint.get_attribute('color'))

    # Get all attributes of a blueprint with recommended values
    for attr in tesla_blueprint:
        print(attr.id, attr.recommended_values)

    # Spawning actors
    transform = carla.Transform(carla.Location(x=230, y=195, z=40), carla.Rotation(pitch=0.0, yaw=180, roll=0.0))
    vehicle = world.spawn_actor(tesla_blueprint, transform)

    # Get recommended spawn points
    spawn_points = world.get_map().get_spawn_points()

    # Spawn camera to the vehicle
    rgb_camera_sensor.set_attribute('image_size_x', '1920')
    rgb_camera_sensor.set_attribute('image_size_y', '1080')
    rgb_camera_sensor.set_attribute('fov', '110')
    cam_location = carla.Location(0.8, 0, 1.7)
    cam_rotation = carla.Rotation(0, 0, 0)
    cam_transform = carla.Transform(cam_location, cam_rotation)
    camera = world.spawn_actor(rgb_camera_sensor, cam_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)

    # Handling camera
    location = vehicle.get_location()
    location.z += 10.0
    vehicle.set_location(location)
    print(vehicle.get_acceleration())
    print(vehicle.get_velocity())

    # Handling vehicle
    vehicle.apply_control(carla.VehicleControl(throttle=0.2, steer=0.0, brake=0.0, hand_brake=False, reverse=False,
                                               manual_gear_shift=False, gear=0))

    world.tick()
    time.sleep(5)
    image_queue = queue.Queue()
    camera.listen(image_queue.put)
    for i in range(10):
        world.tick()
        image = image_queue.get()
        image.save_to_disk('%s/%s.png' % (camera.type_id, image.frame))

    # camera.destroy()
    # vehicle.destroy()

    # Get all actors
    actors = world.get_actors()
    for a in actors:
        if a.type_id in [vehicle.type_id, camera.type_id]:
            a.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
