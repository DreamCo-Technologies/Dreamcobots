import unittest
from tools.buddy_learning_memory import LearningAttempt, record_attempt, lessons_for, regression_warning

class LearningMemoryTests(unittest.TestCase):
    def test_records_and_recovers_lessons(self):
        history = record_attempt([], LearningAttempt("coding", "targeted-study", "failed", .5, .7, "Need more testing", "e1"))
        history = record_attempt(history, LearningAttempt("coding", "sandbox", "passed", .7, .93, "Need more testing", "e2"))
        self.assertEqual(lessons_for(history, "coding"), ["Need more testing"])
        self.assertFalse(regression_warning(history, "coding"))

    def test_detects_regression(self):
        history = record_attempt([], LearningAttempt("vision", "study", "passed", .5, .92, "Add edge cases", "e1"))
        history = record_attempt(history, LearningAttempt("vision", "optimization", "regressed", .92, .81, "Latency optimization hurt quality", "e2"))
        self.assertTrue(regression_warning(history, "vision"))

if __name__ == "__main__":
    unittest.main()
