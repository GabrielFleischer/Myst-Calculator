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

    def test_add_tracks_default_result_buckets(self) -> None:
        """Values are grouped into unit-width buckets starting at zero."""
        stats = RunningStats()

        for value in [0.0, 0.9, 1.0, 2.5]:
            stats.add(value)

        self.assertEqual(
            [
                (bucket.lower_bound, bucket.upper_bound, bucket.count)
                for bucket in stats.buckets
            ],
            [
                (0.0, 1.0, 2),
                (1.0, 2.0, 1),
                (2.0, 3.0, 1),
            ],
        )

    def test_buckets_use_custom_start_and_step(self) -> None:
        """Bucket boundaries use the configured start and step."""
        stats = RunningStats(bucket_start=1.0, bucket_step=0.5)

        for value in [0.75, 1.0, 2.1]:
            stats.add(value)

        self.assertEqual(
            [
                (bucket.lower_bound, bucket.upper_bound, bucket.count)
                for bucket in stats.buckets
            ],
            [
                (0.5, 1.0, 1),
                (1.0, 1.5, 1),
                (1.5, 2.0, 0),
                (2.0, 2.5, 1),
            ],
        )


if __name__ == "__main__":
    unittest.main()
