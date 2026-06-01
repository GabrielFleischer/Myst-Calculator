from dataclasses import dataclass, field
from typing import Callable, Optional
from myst_calculator.core.randomizer import Randomizer
from myst_calculator.core.stats import RunningStats

from math import fabs, nan

type Sampler = Callable[[Randomizer], float]


@dataclass(frozen=True)
class RunnerConfig:

    seed: Optional[int] = None
    batch_size: int = 1000
    sensitivity: float = 0.0000001


@dataclass
class Runner:

    randomizer: Randomizer
    config: RunnerConfig
    sampler: Callable[[Randomizer], float]

    stats: RunningStats = field(default_factory=RunningStats)

    def __init__(
        self,
        sampler: Callable[[Randomizer], float],
        config: RunnerConfig = RunnerConfig(),
    ):
        self.randomizer = Randomizer(config.seed)
        self.config = config
        self.sampler = sampler
        self.stats = RunningStats()

    def run(self) -> RunningStats:
        prev_mean = -1
        while fabs(self.stats.mean - prev_mean) > self.config.sensitivity:
            prev_mean = self.stats.mean
            self.run_batch()

        return self.stats

    def run_batch(self):
        for _ in range(self.config.batch_size):
            self.stats.add(self.sampler(self.randomizer))
