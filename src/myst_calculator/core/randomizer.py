"""Generate random numbers, can be initialized with a seed"""

from random import Random
from typing import Optional, Tuple


class Randomizer:

    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self.rng = Random(seed)

    def next_number(self, start, stop=None, step=1) -> int:
        return self.rng.randrange(start, stop, step)

    def next_choice(self) -> bool:
        return self.rng.choice([True, False])
