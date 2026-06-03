"""Generate reproducible random values."""

from random import Random
from typing import Optional


class Randomizer:
    """Generate random values from an isolated random state."""

    def __init__(self, seed: Optional[int] = None) -> None:
        """Create a randomizer with an optional seed."""
        self._seed = seed
        self._rng = Random(seed)

    @property
    def seed(self) -> Optional[int]:
        """Return the seed used to initialize the randomizer."""
        return self._seed

    def next_number(
        self,
        start: int,
        stop: Optional[int] = None,
        step: int = 1,
    ) -> int:
        """Return a random integer from the configured range."""
        return self._rng.randrange(start, stop, step)

    def next_choice(self) -> bool:
        """Return a random boolean value."""
        return self._rng.choice([True, False])
