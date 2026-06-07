"""Ability roll rules for Myst Calculator."""

from enum import Enum
from math import ceil, floor

from myst_calculator.core.randomizer import Randomizer


class RollType(Enum):
    """Available roll modes for an ability roll."""

    NORMAL = 0
    ADVANTAGE = 1
    DISADVANTAGE = 2


def roll(rand: Randomizer, roll_type: RollType) -> int:
    """Roll a percentile value using the requested roll mode."""
    first_roll = rand.next_number(0, 100)
    if roll_type == RollType.NORMAL:
        return first_roll

    second_roll = rand.next_number(0, 100)
    if roll_type == RollType.ADVANTAGE:
        return min(first_roll, second_roll)
    else:
        return max(first_roll, second_roll)


def roll_on_ability(
    rand: Randomizer, ability: int, roll_type: RollType = RollType.NORMAL
) -> int:
    """Roll against an ability and return successes or failures."""
    result = roll(rand, roll_type)
    diff = ability - result
    return floor(diff / 10) + 1


def opposed_rolls(
    rand: Randomizer,
    ability1: int,
    ability2: int,
    roll_type1: RollType = RollType.NORMAL,
    roll_type2: RollType = RollType.NORMAL,
) -> int:
    """Return the number of successes after an opposed roll. 0 on failure."""
    successes1 = max(0, roll_on_ability(rand, ability1, roll_type1))
    successes2 = max(0, roll_on_ability(rand, ability2, roll_type2))

    return max(0, successes1 - successes2)


def damage_roll(
    rand: Randomizer, dice: int, dice_bonus: int, flat_dmg: int, successes: int
) -> int:
    """Return the damage roll for a given dice and successes."""
    if successes <= 0:
        # Failure
        return 0

    multiplier = ceil(successes / 2)

    total = flat_dmg
    for _ in range(multiplier):
        total += rand.next_number(0, dice + 1) + dice_bonus

    return total
