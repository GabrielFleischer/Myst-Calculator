"""Incremental summary statistics."""

from dataclasses import dataclass
from math import sqrt


@dataclass
class RunningStats:
    """Track mean and standard deviation incrementally."""

    count: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def add(self, value: float) -> None:
        """Add one measurement to the running statistics."""
        self.count += 1

        delta = value - self.mean
        self.mean += delta / self.count
        delta_after = value - self.mean

        self.m2 += delta * delta_after

    @property
    def population_variance(self) -> float:
        """Return the population variance."""
        if self.count == 0:
            return 0.0
        return self.m2 / self.count

    @property
    def sample_variance(self) -> float:
        """Return the sample variance."""
        if self.count < 2:
            return 0.0
        return self.m2 / (self.count - 1)

    @property
    def population_std(self) -> float:
        """Return the population standard deviation."""
        return sqrt(self.population_variance)

    @property
    def sample_std(self) -> float:
        """Return the sample standard deviation."""
        return sqrt(self.sample_variance)
