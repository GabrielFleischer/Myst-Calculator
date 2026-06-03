"""Tests for isolated random number generation."""

import unittest

from myst_calculator.core.randomizer import Randomizer


class RandomizerTest(unittest.TestCase):
    """Test seeded random value generation."""

    def test_same_seed_reproduces_number_sequence(self) -> None:
        """Randomizers with the same seed return the same number sequence."""
        first = Randomizer(seed=123)
        second = Randomizer(seed=123)

        first_values = [first.next_number(0, 100) for _ in range(5)]
        second_values = [second.next_number(0, 100) for _ in range(5)]

        self.assertEqual(first_values, second_values)

    def test_instances_keep_independent_state(self) -> None:
        """Randomizers with the same seed advance independently."""
        first = Randomizer(seed=42)
        second = Randomizer(seed=42)

        self.assertEqual(first.next_number(0, 100), second.next_number(0, 100))
        first.next_number(0, 100)

        self.assertNotEqual(first.next_number(0, 100), second.next_number(0, 100))

    def test_next_choice_returns_boolean(self) -> None:
        """Boolean generation returns a bool value."""
        self.assertIsInstance(Randomizer(seed=1).next_choice(), bool)


if __name__ == "__main__":
    unittest.main()
