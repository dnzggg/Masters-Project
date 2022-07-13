import sys, os, glob, time, queue, re

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

    world = client.get_world()

    original_settings = world.get_settings()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = 0.05
    world.apply_settings(settings)

    file = "C:/Users/Deniz Gorur/PycharmProjects/Masters Project/Scenic examples/records/scenario1.log"
    info = client.show_recorder_file_info(file, True)
    frames = int(re.search(r"Frames: (\d+)", info).group(1))
    print(client.show_recorder_actors_blocked(file, 0, 10))
    client.replay_file(file, 0, 0, 442)

    world.tick()

    blueprint_library = world.get_blueprint_library()
    vehicle = list(world.get_actors().filter('vehicle.tesla.model3'))[0]
    print(vehicle)

    rgb_camera_sensor = blueprint_library.find('sensor.camera.rgb')
    rgb_camera_sensor.set_attribute('image_size_x', '1920')
    rgb_camera_sensor.set_attribute('image_size_y', '1080')
    rgb_camera_sensor.set_attribute('fov', '110')
    cam_location = carla.Location(0.8, 0, 1.7)
    cam_rotation = carla.Rotation(0, 0, 0)
    cam_transform = carla.Transform(cam_location, cam_rotation)
    camera = world.spawn_actor(rgb_camera_sensor, cam_transform, attach_to=vehicle,
                               attachment_type=carla.AttachmentType.Rigid)

    image_queue = queue.Queue()
    camera.listen(image_queue.put)
    for i in range(frames * 2):
        world.tick()
        image = image_queue.get()
        print(vehicle.get_location())
        print(vehicle.get_acceleration())
        w = world.get_snapshot()
        print(w.timestamp)
        # if i % 20 == 0:
        #     image.save_to_disk('%s/%s.png' % (camera.type_id, image.frame))

    vehicles = world.get_actors().filter('vehicle.*')
    sensors = world.get_actors().filter('sensors.*')
    for a in vehicles:
        a.destroy()
    for a in sensors:
        a.destroy()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
