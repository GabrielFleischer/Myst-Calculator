"""Tests for simulation runners."""

import unittest

from myst_calculator.core.randomizer import Randomizer
from myst_calculator.core.runner import Runner, RunnerConfig


class RunnerTest(unittest.TestCase):
    """Test repeated sampler execution."""

    def test_run_batch_records_configured_number_of_samples(self) -> None:
        """Running one batch records the configured number of samples."""
        runner = Runner(
            sampler=lambda _rand: 2.0,
            config=RunnerConfig(seed=1, batch_size=3),
        )

        runner.run_batch()

        self.assertEqual(runner.stats.count, 3)
        self.assertEqual(runner.stats.mean, 2.0)

    def test_run_stops_when_mean_stabilizes(self) -> None:
        """Running to completion returns the accumulated stats."""
        runner = Runner(
            sampler=lambda _rand: 1.0,
            config=RunnerConfig(seed=1, batch_size=2),
        )

        stats = runner.run()

        self.assertIs(stats, runner.stats)
        self.assertEqual(stats.mean, 1.0)
        self.assertEqual(stats.count, 4)

    def test_runner_passes_seeded_randomizer_to_sampler(self) -> None:
        """Runner samplers receive the runner randomizer."""
        seen: list[Randomizer] = []
        runner = Runner(
            sampler=lambda rand: seen.append(rand) or 0.0,
            config=RunnerConfig(seed=99, batch_size=1),
        )

        runner.run_batch()

        self.assertEqual(seen, [runner.randomizer])
        self.assertEqual(runner.randomizer.seed, 99)

    def test_runner_configures_result_buckets(self) -> None:
        """Runner statistics use the configured bucket boundaries."""
        runner = Runner(
            sampler=lambda _rand: 2.0,
            config=RunnerConfig(bucket_start=1.0, bucket_step=0.5),
        )

        self.assertEqual(runner.stats.bucket_start, 1.0)
        self.assertEqual(runner.stats.bucket_step, 0.5)


if __name__ == "__main__":
    unittest.main()
