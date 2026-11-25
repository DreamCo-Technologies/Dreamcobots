"""Course-track contract checks for O*NET unseen assessment wording."""
from __future__ import annotations

import unittest

from buddy.learning.course_track_registry import load_course_lessons


class CourseTrackRegistryTests(unittest.TestCase):
    def test_onet_task_lessons_require_an_unseen_assessment(self):
        lessons = load_course_lessons()
        onet_lessons = [row for row in lessons if row.track_id.lower() == "onet"]
        self.assertTrue(onet_lessons)
        self.assertTrue(all("unseen assessment" in row.assessment.lower() for row in onet_lessons))


if __name__ == "__main__":
    unittest.main()
