"""Run samplers until their running mean stabilizes."""

from dataclasses import dataclass, field
from math import fabs
from typing import Callable, Optional

from myst_calculator.core.randomizer import Randomizer
from myst_calculator.core.stats import RunningStats

type Sampler = Callable[[Randomizer], float]


@dataclass(frozen=True)
class RunnerConfig:
    """Configure a simulation runner."""

    seed: Optional[int] = None
    batch_size: int = 1000
    sensitivity: float = 0.0000001
    bucket_start: float = 0.0
    bucket_step: float = 1.0


@dataclass
class Runner:
    """Run a sampler and track its statistics."""

    randomizer: Randomizer
    config: RunnerConfig
    sampler: Callable[[Randomizer], float]

    stats: RunningStats = field(default_factory=RunningStats)

    def __init__(
        self,
        sampler: Callable[[Randomizer], float],
        config: RunnerConfig = RunnerConfig(),
    ) -> None:
        """Create a runner for the provided sampler."""
        self.randomizer = Randomizer(config.seed)
        self.config = config
        self.sampler = sampler
        self.stats = RunningStats(
            bucket_start=config.bucket_start,
            bucket_step=config.bucket_step,
        )

    def run(self) -> RunningStats:
        """Run batches until the running mean change is within sensitivity."""
        prev_mean = -1
        while fabs(self.stats.mean - prev_mean) > self.config.sensitivity:
            prev_mean = self.stats.mean
            self.run_batch()

        return self.stats

    def run_batch(self) -> None:
        """Run one configured batch of samples."""
        for _ in range(self.config.batch_size):
            self.stats.add(self.sampler(self.randomizer))
