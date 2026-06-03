"""High-level Myst simulation samplers. All samplers are written here."""

from myst_calculator.core.ability_roll import RollType, opposed_rolls
from myst_calculator.core.runner import Sampler


def opposed_roll_sampler(
    ability1: int,
    ability2: int,
    roll_type1: RollType = RollType.NORMAL,
    roll_type2: RollType = RollType.NORMAL,
) -> Sampler:
    """Create a sampler for opposed ability rolls."""
    return lambda rand: float(
        opposed_rolls(rand, ability1, ability2, roll_type1, roll_type2)
    )
