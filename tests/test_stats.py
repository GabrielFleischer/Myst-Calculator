"""Tests for running summary statistics."""

import unittest

from myst_calculator.core.stats import RunningStats


class RunningStatsTest(unittest.TestCase):
    """Test incremental mean and standard deviation."""

    def test_empty_stats_return_zero_variance(self) -> None:
        """Empty stats return zero for variance and standard deviation."""
        stats = RunningStats()

        self.assertEqual(stats.population_variance, 0.0)
        self.assertEqual(stats.sample_variance, 0.0)
        self.assertEqual(stats.population_std, 0.0)
        self.assertEqual(stats.sample_std, 0.0)

    def test_add_tracks_mean_and_population_standard_deviation(self) -> None:
        """Adding values updates mean and population standard deviation."""
        stats = RunningStats()

        for value in [2, 4, 4, 4, 5, 5, 7, 9]:
            stats.add(value)

        self.assertEqual(stats.count, 8)
        self.assertEqual(stats.mean, 5.0)
        self.assertEqual(stats.population_variance, 4.0)
        self.assertEqual(stats.population_std, 2.0)

    def test_add_tracks_sample_standard_deviation(self) -> None:
        """Adding values updates sample variance and standard deviation."""
        stats = RunningStats()

        for value in [1, 2, 3]:
            stats.add(value)

        self.assertEqual(stats.sample_variance, 1.0)
        self.assertEqual(stats.sample_std, 1.0)


if __name__ == "__main__":
    unittest.main()
