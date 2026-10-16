"""Checks for the original analytical example; not human-listening data."""
from __future__ import annotations
import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("candidate_protocol_under_test", ROOT / "code/candidate_protocol.py")
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

class CandidateChecks(unittest.TestCase):
    def test_bank_has_51_unique_settings(self):
        bank = m.candidate_bank()
        self.assertEqual(len(bank), 51)
        self.assertEqual(len({(x.vocal_db, x.band_db) for x in bank}), 51)
        self.assertEqual([x.id for x in bank], list(range(1, 52)))

    def test_absolute_protection_and_reference_costs(self):
        bank = {(x.vocal_db, x.band_db): x for x in m.candidate_bank()}
        self.assertTrue(bank[(0, -1.5)].target_pass)
        self.assertFalse(bank[(0, -1.5)].protection_pass)
        self.assertAlmostEqual(bank[(0, -1.5)].protected_distance_db, 1.5)
        self.assertAlmostEqual(bank[(1.5, 0)].J, 0.3)
        self.assertAlmostEqual(bank[(1.4, -0.1)].J, 0.7)

    def test_same_pool_for_both_directions(self):
        settings = None
        for target in (-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5):
            bank = m.candidate_bank(target)
            current = [(x.id, x.vocal_db, x.band_db) for x in bank]
            if settings is None:
                settings = current
            self.assertEqual(settings, current)
            chosen = m.select(bank, "full")
            self.assertIsNotNone(chosen)
            self.assertTrue(chosen.target_pass and chosen.protection_pass)

    def test_zero_target_selects_no_change(self):
        x = m.select(m.candidate_bank(0), "full")
        self.assertEqual((x.vocal_db, x.band_db), (0, 0))

    def test_fixed_random_order(self):
        bank = m.candidate_bank()
        self.assertEqual(m.select(bank, "baseline"), m.select(bank, "baseline"))
        for name in ("operation", "protection", "full"):
            self.assertEqual(m.select(bank, name), m.select(bank, name))

    def test_no_candidate_meeting_an_outside_target(self):
        bank = m.candidate_bank(99)
        for name in ("baseline", "operation", "protection", "full"):
            self.assertIsNone(m.select(bank, name))
        # This is failure within this finite bank, not a proof of global infeasibility.

    def test_invalid_tolerance_is_rejected(self):
        for kwargs in ({"target_tolerance": -1}, {"protection_tolerance": 0}, {"protection_tolerance": -1}):
            with self.assertRaises(ValueError):
                m.candidate_bank(**kwargs)

    def test_illustrative_scoring_logic(self):
        self.assertTrue(m.listening_pass(0, [0, 2], True, True))
        self.assertFalse(m.listening_pass(2, [0, 2], True, True))
        self.assertFalse(m.listening_pass(0, [0, 3], True, True))
        self.assertFalse(m.listening_pass(0, [0, 2], False, True))
        self.assertFalse(m.listening_pass(None, [None], None, False))
        self.assertIsNone(m.listening_pass(None, [0, 2], True, True))
        self.assertIsNone(m.listening_pass(0, [None], True, True))
        with self.assertRaises(ValueError):
            m.listening_pass(4, [0], True, True)

    def test_task_summary(self):
        self.assertEqual(m.task_label([True] * 8 + [False] * 4, 12), "accepted")
        self.assertEqual(m.task_label([True] * 8 + [None] * 4, 12), "insufficient_evidence")
        self.assertEqual(m.task_label([True] * 7 + [False] * 5, 12), "not_accepted")
        with self.assertRaises(ValueError):
            m.task_label([], 0)

    def test_original_self_test(self):
        result = m.self_test()
        self.assertEqual(result["candidate_count"], 51)
        self.assertEqual(result["checks"], "passed")

if __name__ == "__main__":
    unittest.main()
