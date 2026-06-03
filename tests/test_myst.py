"""Tests for Myst rolling logic."""

import unittest
from collections.abc import Iterable

from myst_calculator.core.ability_roll import (
    RollType,
    opposed_rolls,
    roll,
    roll_on_ability,
)
from myst_calculator.core.myst import opposed_roll_sampler
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


class OpposedRollTest(unittest.TestCase):
    """Test opposed roll resolution."""

    def test_opposed_rolls_subtract_second_successes_from_first(self) -> None:
        """Opposed rolls return remaining successes for the first ability."""
        rand = FixedRandomizer([20, 45])

        self.assertEqual(opposed_rolls(rand, ability1=60, ability2=55), 3)

    def test_opposed_rolls_do_not_return_negative_successes(self) -> None:
        """Opposed rolls clamp losing results to zero."""
        rand = FixedRandomizer([70, 10])

        self.assertEqual(opposed_rolls(rand, ability1=40, ability2=80), 0)

    def test_opposed_rolls_support_roll_types_for_both_sides(self) -> None:
        """Opposed rolls use the configured roll type for each ability."""
        rand = FixedRandomizer([20, 70, 30, 90])

        self.assertEqual(
            opposed_rolls(
                rand,
                ability1=60,
                ability2=60,
                roll_type1=RollType.ADVANTAGE,
                roll_type2=RollType.DISADVANTAGE,
            ),
            5,
        )


class OpposedRollSamplerTest(unittest.TestCase):
    """Test high-level opposed roll sampler creation."""

    def test_opposed_roll_sampler_returns_float_results(self) -> None:
        """Opposed roll samplers adapt integer outcomes to float samples."""
        sampler = opposed_roll_sampler(60, 55)

        self.assertEqual(sampler(FixedRandomizer([20, 45])), 3.0)


if __name__ == "__main__":
    unittest.main()
