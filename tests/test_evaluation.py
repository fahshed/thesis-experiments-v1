import unittest
from src.utils.evaluation import compute_exact_match, compute_f1, compute_overlap

class TestEvaluation(unittest.TestCase):
    def test_compute_exact_match(self):
        self.assertEqual(compute_exact_match("Yes", "yes"), 1.0)
        self.assertEqual(compute_exact_match("3.9", "3.9"), 1.0)
        self.assertEqual(compute_exact_match("He knows python", "He knows Python."), 1.0)
        self.assertEqual(compute_exact_match("Yes", "No"), 0.0)

    def test_compute_f1(self):
        pred = "Python, Java"
        truth = "Python Java C++"
        # pred has 2 tokens. truth has 3 tokens. overlap is 2.
        # prec = 2/2 = 1.0
        # rec = 2/3 = 0.666
        # f1 = 2 * (1*0.666) / 1.666 = 0.8
        f1_score = compute_f1(pred, truth)
        self.assertAlmostEqual(f1_score, 0.8, places=2)

    def test_compute_overlap(self):
        pred = "Python and Java"
        truth = "Python Java C++"
        # Overlap calculates intersection out of truth len:
        # pred tokens: python, and, java
        # truth tokens: python, java, c++
        # intersection = python, java = 2. truth total = 3
        # result = 2/3 = 0.666
        overlap_score = compute_overlap(pred, truth)
        self.assertAlmostEqual(overlap_score, 0.666, places=2)

if __name__ == "__main__":
    unittest.main()
