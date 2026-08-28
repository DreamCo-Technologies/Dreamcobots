import math

import pytest

from buddy_os.intelligence.geometric_reasoning import (
    AABB, RigidTransform2D, Vec3, angle_between, shortest_path,
    spatial_relation, transform_invariant_distance,
)


def test_vector_algebra_and_cross_product():
    a, b = Vec3(1, 2, 3), Vec3(4, 5, 6)
    assert a + b == Vec3(5, 7, 9)
    assert a.dot(b) == 32
    assert a.cross(b) == Vec3(-3, 6, -3)


def test_rigid_transform_preserves_distance_and_round_trips():
    transform = RigidTransform2D(math.pi / 2, 10, -2)
    a, b = Vec3(1, 2), Vec3(4, 6)
    assert transform_invariant_distance(a, b, transform)
    assert transform.inverse().apply(transform.apply(a)).distance_to(a) < 1e-8


def test_spatial_relations_and_bounds():
    assert spatial_relation(Vec3(5, 0), Vec3(0, 0)) == "right"
    box = AABB(Vec3(0, 0, 0), Vec3(2, 2, 2))
    assert box.contains(Vec3(1, 1, 1))
    assert box.intersects(AABB(Vec3(1, 1, 1), Vec3(3, 3, 3)))


def test_angle_and_shortest_path():
    assert abs(angle_between(Vec3(1, 0), Vec3(0, 1)) - math.pi / 2) < 1e-9
    graph = {"A": [("B", 1), ("C", 5)], "B": [("C", 2)], "C": []}
    assert shortest_path(graph, "A", "C") == (3, ["A", "B", "C"])


def test_invalid_geometry_is_rejected():
    with pytest.raises(ValueError):
        Vec3(0, 0, 0).normalized()
    with pytest.raises(ValueError):
        shortest_path({"A": [("B", -1)], "B": []}, "A", "B")
