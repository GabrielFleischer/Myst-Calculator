"""Tests for Myst rolling logic."""

import unittest
from collections.abc import Iterable

from myst_calculator.core.ability_roll import RollType, roll, roll_on_ability
from myst_calculator.core.randomizer import Randomizer


class FixedRandomizer(Randomizer):
    """Return predefined numbers for deterministic roll tests."""

    def __init__(self, values: Iterable[int]) -> None:
        """Create a randomizer from the provided values."""
        super().__init__()
        self._values = iter(values)

    def next_number(
        self,
        _1: int,
        _2: int | None = None,
        _3: int = 1,
    ) -> int:
        """Return the next predefined number."""
        return next(self._values)


class RollTest(unittest.TestCase):
    """Test roll behavior for each roll type."""

    def test_normal_roll_uses_first_value(self) -> None:
        """A normal roll returns the first generated value."""
        rand = FixedRandomizer([42])

        self.assertEqual(roll(rand, RollType.NORMAL), 42)

    def test_advantage_roll_uses_lowest_value(self) -> None:
        """An advantage roll returns the lower of two generated values."""
        rand = FixedRandomizer([24, 86])

        self.assertEqual(roll(rand, RollType.ADVANTAGE), 24)

    def test_disadvantage_roll_uses_highest_value(self) -> None:
        """A disadvantage roll returns the higher of two generated values."""
        rand = FixedRandomizer([24, 86])

        self.assertEqual(roll(rand, RollType.DISADVANTAGE), 86)


class RollOnAbilityTest(unittest.TestCase):
    """Test ability roll success calculation."""

    def test_roll_on_ability_counts_successes(self) -> None:
        """A roll below the ability returns positive successes."""
        rand = FixedRandomizer([35])

        self.assertEqual(roll_on_ability(rand, ability=60), 3)

    def test_roll_on_ability_counts_failures(self) -> None:
        """A roll above the ability returns failures as a negative value."""
        rand = FixedRandomizer([82])

        self.assertEqual(roll_on_ability(rand, ability=40), -4)

    def test_roll_on_ability_supports_advantage(self) -> None:
        """Ability rolls support advantage and use the higher rolled value."""
        rand = FixedRandomizer([20, 70])

        self.assertEqual(
            roll_on_ability(rand, ability=60, roll_type=RollType.ADVANTAGE),
            5,
        )


if __name__ == "__main__":
    unittest.main()
