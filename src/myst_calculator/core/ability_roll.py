from enum import Enum

from myst_calculator.core.randomizer import Randomizer
from math import floor


class RollType(Enum):
    NORMAL = 0
    ADVANTAGE = 1
    DISADVANTAGE = 2


def roll(rand: Randomizer, roll_type: RollType):
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
    """Make a roll on the ability and produce the number of successes. (or failures if negative)."""
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

    successes1 = max(0, roll_on_ability(rand, ability1, roll_type1))
    successes2 = max(0, roll_on_ability(rand, ability2, roll_type2))

    return max(0, successes1 - successes2)
