"""Open-source geometric reasoning primitives for Buddy.

Pure-Python, dependency-light geometry kernel intended to sit underneath the
DreamCo ontology and digital twin. It handles 2D/3D points, vectors, rigid
transforms, spatial relations, distances, axis-aligned bounds, and shortest
paths. It deliberately contains no execution or permission logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, hypot, sin, sqrt
from typing import Iterable, Mapping, Sequence

_EPS = 1e-9


@dataclass(frozen=True)
class Vec3:
    x: float
    y: float
    z: float = 0.0

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(self.y * other.z - self.z * other.y,
                    self.z * other.x - self.x * other.z,
                    self.x * other.y - self.y * other.x)

    def norm(self) -> float:
        return sqrt(self.dot(self))

    def normalized(self) -> "Vec3":
        n = self.norm()
        if n < _EPS:
            raise ValueError("Cannot normalize a zero-length vector")
        return self * (1.0 / n)

    def distance_to(self, other: "Vec3") -> float:
        return (self - other).norm()


@dataclass(frozen=True)
class AABB:
    minimum: Vec3
    maximum: Vec3

    def __post_init__(self) -> None:
        if (self.minimum.x > self.maximum.x or self.minimum.y > self.maximum.y
                or self.minimum.z > self.maximum.z):
            raise ValueError("AABB minimum must not exceed maximum")

    def contains(self, p: Vec3) -> bool:
        return (self.minimum.x - _EPS <= p.x <= self.maximum.x + _EPS
                and self.minimum.y - _EPS <= p.y <= self.maximum.y + _EPS
                and self.minimum.z - _EPS <= p.z <= self.maximum.z + _EPS)

    def intersects(self, other: "AABB") -> bool:
        return (self.minimum.x <= other.maximum.x + _EPS and other.minimum.x <= self.maximum.x + _EPS
                and self.minimum.y <= other.maximum.y + _EPS and other.minimum.y <= self.maximum.y + _EPS
                and self.minimum.z <= other.maximum.z + _EPS and other.minimum.z <= self.maximum.z + _EPS)

    def center(self) -> Vec3:
        return Vec3((self.minimum.x + self.maximum.x) / 2,
                    (self.minimum.y + self.maximum.y) / 2,
                    (self.minimum.z + self.maximum.z) / 2)


@dataclass(frozen=True)
class RigidTransform2D:
    """SE(2) transform: rotation followed by translation."""
    theta: float = 0.0
    tx: float = 0.0
    ty: float = 0.0

    def apply(self, p: Vec3) -> Vec3:
        c, s = cos(self.theta), sin(self.theta)
        return Vec3(c * p.x - s * p.y + self.tx,
                    s * p.x + c * p.y + self.ty,
                    p.z)

    def inverse(self) -> "RigidTransform2D":
        c, s = cos(self.theta), sin(self.theta)
        return RigidTransform2D(-self.theta, -c * self.tx - s * self.ty,
                               s * self.tx - c * self.ty)

    def compose(self, other: "RigidTransform2D") -> "RigidTransform2D":
        p = self.apply(Vec3(other.tx, other.ty))
        return RigidTransform2D(self.theta + other.theta, p.x, p.y)


@dataclass(frozen=True)
class SpatialRelation:
    subject: str
    relation: str
    reference: str
    confidence: float = 1.0
    distance: float | None = None


def angle_between(a: Vec3, b: Vec3) -> float:
    """Return the unsigned angle in radians, robust to floating point drift."""
    na, nb = a.norm(), b.norm()
    if na < _EPS or nb < _EPS:
        raise ValueError("Angle is undefined for a zero-length vector")
    value = max(-1.0, min(1.0, a.dot(b) / (na * nb)))
    from math import acos
    return acos(value)


def spatial_relation(subject: Vec3, reference: Vec3, tolerance: float = 1e-6) -> str:
    dx, dy, dz = subject.x - reference.x, subject.y - reference.y, subject.z - reference.z
    if abs(dx) <= tolerance and abs(dy) <= tolerance and abs(dz) <= tolerance:
        return "coincident"
    axes = [(abs(dx), "right" if dx > 0 else "left"),
            (abs(dy), "above" if dy > 0 else "below"),
            (abs(dz), "front" if dz > 0 else "behind")]
    return max(axes, key=lambda item: item[0])[1]


def shortest_path(graph: Mapping[str, Iterable[tuple[str, float]]], start: str, goal: str) -> tuple[float, list[str]]:
    """Dijkstra shortest path over a weighted spatial/navigation graph."""
    import heapq
    if start not in graph or goal not in graph:
        raise KeyError("start and goal must exist in graph")
    distances = {start: 0.0}
    previous: dict[str, str] = {}
    queue = [(0.0, start)]
    while queue:
        distance, node = heapq.heappop(queue)
        if distance > distances.get(node, float("inf")) + _EPS:
            continue
        if node == goal:
            path = [goal]
            while path[-1] != start:
                path.append(previous[path[-1]])
            path.reverse()
            return distance, path
        for neighbor, weight in graph[node]:
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            candidate = distance + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
    return float("inf"), []


def transform_invariant_distance(a: Vec3, b: Vec3, transform: RigidTransform2D) -> bool:
    """Sanity check for the key rigid-motion invariant: distances are preserved."""
    return abs(a.distance_to(b) - transform.apply(a).distance_to(transform.apply(b))) <= 1e-8
