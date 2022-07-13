param map = localPath('Town05.xodr')
param carla_map = 'Town05'
param time_step = 1.0/10

model scenic.domains.driving.model

EGO_MODEL = "vehicle.tesla.model3"
OTHER_MODEL = "vehicle.toyota.prius"

behavior PullIntoRoad():
    while (distance from self to ego) > 15:
        wait
    do FollowLaneBehavior(laneToFollow=ego.lane)

ego = Car with behavior DriveAvoidingCollisions(avoidance_threshold=5),
        with blueprint EGO_MODEL

rightCurb = ego.laneGroup.curb
spot = OrientedPoint on visible rightCurb
badAngle = Uniform(1.0, -1.0) * Range(10, 20) deg
parkedCar = Car left of spot by 0.5,
                facing badAngle relative to roadDirection,
                with behavior PullIntoRoad,
                with blueprint OTHER_MODEL

require (distance to parkedCar) > 20

monitor StopAfterInteraction:
	for i in range(50):
		wait
	while ego.speed > 2:
		wait
	for i in range(50):
		wait
	terminate

monitor StopAfterSpeed:
    for i in range(50):
        wait
    print("Speed: " + str(ego.speed))
    while ego.speed < 10:
        wait
    for i in range(50):
        wait
    terminate