"""Advanced, dependency-light geometry primitives for Buddy.

This module complements geometric_reasoning.py with SE(3)-style poses,
quaternions, planes, rays, segments, and 2D polygon predicates. It is a
mathematical kernel only: no external side effects or execution authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import acos, sqrt
from typing import Sequence

from .geometric_reasoning import Vec3

_EPS = 1e-9


@dataclass(frozen=True)
class Quaternion:
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def norm(self) -> float:
        return sqrt(self.w*self.w + self.x*self.x + self.y*self.y + self.z*self.z)

    def normalized(self) -> "Quaternion":
        n = self.norm()
        if n < _EPS:
            raise ValueError("Cannot normalize a zero quaternion")
        return Quaternion(self.w/n, self.x/n, self.y/n, self.z/n)

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(
            self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
            self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
            self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
            self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w,
        )

    def rotate(self, vector: Vec3) -> Vec3:
        q = self.normalized()
        v = Quaternion(0.0, vector.x, vector.y, vector.z)
        r = q * v * q.conjugate()
        return Vec3(r.x, r.y, r.z)


@dataclass(frozen=True)
class Pose3D:
    position: Vec3 = Vec3(0.0, 0.0, 0.0)
    orientation: Quaternion = Quaternion()

    def transform_point(self, point: Vec3) -> Vec3:
        return self.orientation.rotate(point) + self.position

    def inverse_transform_point(self, point: Vec3) -> Vec3:
        return self.orientation.normalized().conjugate().rotate(point - self.position)


@dataclass(frozen=True)
class Plane:
    point: Vec3
    normal: Vec3

    def __post_init__(self) -> None:
        if self.normal.norm() < _EPS:
            raise ValueError("Plane normal cannot be zero")

    def signed_distance(self, point: Vec3) -> float:
        return (point - self.point).dot(self.normal.normalized())


@dataclass(frozen=True)
class Ray3D:
    origin: Vec3
    direction: Vec3

    def __post_init__(self) -> None:
        if self.direction.norm() < _EPS:
            raise ValueError("Ray direction cannot be zero")

    def point_at(self, distance: float) -> Vec3:
        return self.origin + self.direction.normalized() * distance


def ray_plane_intersection(ray: Ray3D, plane: Plane) -> Vec3 | None:
    direction = ray.direction.normalized()
    normal = plane.normal.normalized()
    denominator = direction.dot(normal)
    if abs(denominator) < _EPS:
        return None
    distance = (plane.point - ray.origin).dot(normal) / denominator
    if distance < -_EPS:
        return None
    return ray.origin + direction * distance


def point_in_polygon(point: tuple[float, float], polygon: Sequence[tuple[float, float]]) -> bool:
    """Ray-casting point-in-polygon predicate; boundary points count as inside."""
    if len(polygon) < 3:
        raise ValueError("Polygon requires at least three vertices")
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        cross = (x - xi) * (yj - yi) - (y - yi) * (xj - xi)
        if abs(cross) <= _EPS and min(xi, xj)-_EPS <= x <= max(xi, xj)+_EPS and min(yi, yj)-_EPS <= y <= max(yi, yj)+_EPS:
            return True
        intersects = ((yi > y) != (yj > y)) and (x < (xj-xi) * (y-yi) / ((yj-yi) or _EPS) + xi)
        if intersects:
            inside = not inside
        j = i
    return inside


def polygon_signed_area(polygon: Sequence[tuple[float, float]]) -> float:
    if len(polygon) < 3:
        raise ValueError("Polygon requires at least three vertices")
    return 0.5 * sum(polygon[i][0] * polygon[(i+1) % len(polygon)][1] - polygon[(i+1) % len(polygon)][0] * polygon[i][1] for i in range(len(polygon)))


def quaternion_angular_distance(a: Quaternion, b: Quaternion) -> float:
    """Shortest orientation distance in radians."""
    qa, qb = a.normalized(), b.normalized()
    dot = abs(qa.w*qb.w + qa.x*qb.x + qa.y*qb.y + qa.z*qb.z)
    return 2.0 * acos(max(-1.0, min(1.0, dot)))
