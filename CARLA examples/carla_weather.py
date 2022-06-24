import sys, os, glob, time

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

    # Set weather (this does not affect physics. It only changes the visual captured by the camera sensors)
    weather = carla.WeatherParameters(
        cloudiness=80.0,
        precipitation=30.0,
        sun_altitude_angle=70.0)

    world.set_weather(weather)

    print(world.get_weather())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
