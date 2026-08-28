import math

from buddy_os.intelligence.geometric_frontier import (
    Plane, Pose3D, Quaternion, Ray3D, point_in_polygon,
    polygon_signed_area, quaternion_angular_distance, ray_plane_intersection,
)
from buddy_os.intelligence.geometric_reasoning import Vec3


def test_pose_round_trip():
    pose = Pose3D(Vec3(10, -2, 3), Quaternion(0.9238795, 0, 0, 0.3826834))
    point = Vec3(2, 1, 4)
    assert pose.inverse_transform_point(pose.transform_point(point)).distance_to(point) < 1e-5


def test_ray_plane_intersection():
    hit = ray_plane_intersection(Ray3D(Vec3(0, 0, 1), Vec3(0, 0, -1)), Plane(Vec3(0, 0, 0), Vec3(0, 0, 1)))
    assert hit is not None
    assert hit.distance_to(Vec3(0, 0, 0)) < 1e-9


def test_polygon_predicates_and_area():
    square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert point_in_polygon((1, 1), square)
    assert not point_in_polygon((3, 1), square)
    assert abs(polygon_signed_area(square) - 4) < 1e-9


def test_quaternion_orientation_distance():
    a = Quaternion()
    b = Quaternion(math.cos(math.pi/4), 0, 0, math.sin(math.pi/4))
    assert abs(quaternion_angular_distance(a, b) - math.pi/2) < 1e-7
