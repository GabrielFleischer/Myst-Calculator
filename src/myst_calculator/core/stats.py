"""Incremental summary statistics."""

from dataclasses import dataclass, field
from math import floor, sqrt


@dataclass(frozen=True)
class ResultBucket:
    """Describe one result bucket and its observed sample count."""

    lower_bound: float
    upper_bound: float
    count: int


@dataclass
class RunningStats:
    """Track mean and standard deviation incrementally."""

    count: int = 0
    mean: float = 0.0
    m2: float = 0.0
    bucket_start: float = 0.0
    bucket_step: float = 1.0
    _bucket_counts: dict[int, int] = field(default_factory=dict)

    def add(self, value: float) -> None:
        """Add one measurement to the running statistics."""
        self.count += 1
        bucket_index = floor((value - self.bucket_start) / self.bucket_step)
        self._bucket_counts[bucket_index] = (
            self._bucket_counts.get(bucket_index, 0) + 1
        )

        delta = value - self.mean
        self.mean += delta / self.count
        delta_after = value - self.mean

        self.m2 += delta * delta_after

    @property
    def buckets(self) -> tuple[ResultBucket, ...]:
        """Return observed buckets, including empty gaps, in ascending order."""
        if not self._bucket_counts:
            return ()

        first_index = min(self._bucket_counts)
        last_index = max(self._bucket_counts)
        return tuple(
            ResultBucket(
                lower_bound=self.bucket_start + index * self.bucket_step,
                upper_bound=self.bucket_start + (index + 1) * self.bucket_step,
                count=self._bucket_counts.get(index, 0),
            )
            for index in range(first_index, last_index + 1)
        )

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
