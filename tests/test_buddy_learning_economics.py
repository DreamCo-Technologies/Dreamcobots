import unittest
from tools.buddy_learning_economics import LearningOption, choose_options

class LearningEconomicsTests(unittest.TestCase):
    def test_prefers_high_utility_option(self):
        good = LearningOption("targeted-course", .8, 10, .01, .9)
        wasteful = LearningOption("huge-library", .8, 10000, 10, .9)
        self.assertEqual(choose_options([wasteful, good], 1, 1)[0].name, "targeted-course")

    def test_respects_budget(self):
        a = LearningOption("a", .8, 100, .1)
        b = LearningOption("b", .7, 100, .1)
        self.assertEqual(len(choose_options([a, b], .25, 5)), 1)

if __name__ == "__main__":
    unittest.main()
