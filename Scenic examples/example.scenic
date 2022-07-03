# creates an ego vehicle and a car; car facing the ego vehicle

from scenic.simulators.gta.model import Car
ego = Car
c2 = Car offset by Range(-10, 10) @ Range(20, 40)
require c2 can see ego