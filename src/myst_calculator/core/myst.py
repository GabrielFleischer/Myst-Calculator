"""High-level Myst simulation samplers. All samplers are written here."""

from myst_calculator.core.randomizer import Randomizer
from myst_calculator.core.roll import RollType, damage_roll, opposed_rolls
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


def attack_action_sampler(
    attack: int,
    defense: int,
    dice: int,
    dice_bonus: int,
    flat_dmg: int,
    attack_roll_type: RollType = RollType.NORMAL,
    defense_roll_type: RollType = RollType.NORMAL,
) -> Sampler:
    """Create a sampler for an attack action's damage."""

    def attack_action(rand: Randomizer) -> float:
        successes = opposed_rolls(
            rand,
            attack,
            defense,
            attack_roll_type,
            defense_roll_type,
        )
        dmg = damage_roll(rand, dice, dice_bonus, flat_dmg, successes)
        return float(dmg)

    return attack_action
