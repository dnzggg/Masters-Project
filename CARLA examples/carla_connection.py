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

    # World connection and map load
    world = client.load_world('Town01')

    # Getting available maps
    maps = client.get_available_maps()
    print(maps)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
