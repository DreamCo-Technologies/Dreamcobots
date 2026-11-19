import unittest
from datetime import datetime, timezone
from tools.dreamco_rotating_operations import LANES, rotation_index


class DreamCoRotationTests(unittest.TestCase):
    def test_every_lane_is_reached_in_one_complete_cycle(self):
        start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        indexes = [rotation_index(datetime.fromtimestamp(start.timestamp() + 300 * n, timezone.utc)) for n in range(len(LANES))]
        self.assertEqual(indexes, list(range(len(LANES))))

    def test_rotation_is_stable_within_a_five_minute_slot(self):
        first = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        second = datetime(2026, 1, 1, 0, 4, 59, tzinfo=timezone.utc)
        self.assertEqual(rotation_index(first), rotation_index(second))

    def test_rotation_advances_at_the_next_five_minute_boundary(self):
        first = datetime(2026, 1, 1, 0, 4, 59, tzinfo=timezone.utc)
        second = datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc)
        self.assertNotEqual(rotation_index(first), rotation_index(second))

    def test_all_lanes_have_unique_ids_and_commands(self):
        ids = [lane["id"] for lane in LANES]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(lane["commands"] for lane in LANES))


if __name__ == "__main__":
    unittest.main()
