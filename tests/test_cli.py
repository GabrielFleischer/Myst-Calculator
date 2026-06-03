"""Tests for the command-line interface."""

import argparse
import contextlib
import io
import unittest
from unittest.mock import Mock, patch

from myst_calculator.cli.app import (
    build_runner_config,
    build_parser,
    main,
    parse_positive_float,
    parse_positive_int,
    parse_roll_type,
)
from myst_calculator.core.ability_roll import RollType
from myst_calculator.core.runner import RunnerConfig


class CliParserTest(unittest.TestCase):
    """Test command-line parser helpers."""

    def test_parse_positive_int_accepts_positive_values(self) -> None:
        """Positive integer parsing accepts values greater than zero."""
        self.assertEqual(parse_positive_int("12"), 12)

    def test_parse_positive_int_rejects_zero(self) -> None:
        """Positive integer parsing rejects zero."""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_positive_int("0")

    def test_parse_positive_int_rejects_non_integer_text(self) -> None:
        """Positive integer parsing rejects text that is not an integer."""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_positive_int("many")

    def test_parse_positive_float_accepts_positive_values(self) -> None:
        """Positive float parsing accepts values greater than zero."""
        self.assertEqual(parse_positive_float("0.001"), 0.001)

    def test_parse_positive_float_rejects_zero(self) -> None:
        """Positive float parsing rejects zero."""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_positive_float("0")

    def test_parse_positive_float_rejects_non_numeric_text(self) -> None:
        """Positive float parsing rejects text that is not a number."""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_positive_float("small")

    def test_parse_roll_type_accepts_enum_names(self) -> None:
        """Roll type parsing accepts valid enum entry names."""
        self.assertEqual(parse_roll_type("ADVANTAGE"), RollType.ADVANTAGE)

    def test_parse_roll_type_is_case_insensitive(self) -> None:
        """Roll type parsing accepts lowercase enum entry names."""
        self.assertEqual(parse_roll_type("normal"), RollType.NORMAL)

    def test_parse_roll_type_rejects_unknown_values(self) -> None:
        """Roll type parsing rejects values outside the enum."""
        with self.assertRaises(argparse.ArgumentTypeError):
            parse_roll_type("unknown")

    def test_opposed_command_defaults_roll_types_to_normal(self) -> None:
        """The opposed command defaults both roll types to normal."""
        parser = build_parser()

        args = parser.parse_args(["opposed", "40", "60"])

        self.assertEqual(args.ability1, 40)
        self.assertEqual(args.ability2, 60)
        self.assertEqual(args.type1, RollType.NORMAL)
        self.assertEqual(args.type2, RollType.NORMAL)
        self.assertEqual(args.batch_size, RunnerConfig.batch_size)
        self.assertEqual(args.precision, RunnerConfig.sensitivity)
        self.assertIsNone(args.seed)

    def test_opposed_command_accepts_roll_type_options(self) -> None:
        """The opposed command accepts both optional roll type arguments."""
        parser = build_parser()

        args = parser.parse_args(
            [
                "opposed",
                "40",
                "60",
                "--type1",
                "ADVANTAGE",
                "--type2",
                "DISADVANTAGE",
            ]
        )

        self.assertEqual(args.type1, RollType.ADVANTAGE)
        self.assertEqual(args.type2, RollType.DISADVANTAGE)

    def test_opposed_command_accepts_shared_runner_options(self) -> None:
        """The opposed command accepts options shared by all subcommands."""
        parser = build_parser()

        args = parser.parse_args(
            [
                "opposed",
                "40",
                "60",
                "--batch-size",
                "500",
                "--precision",
                "0.01",
                "--seed",
                "123",
            ]
        )

        self.assertEqual(args.batch_size, 500)
        self.assertEqual(args.precision, 0.01)
        self.assertEqual(args.seed, 123)

    def test_opposed_command_rejects_non_positive_abilities(self) -> None:
        """The opposed command rejects non-positive abilities."""
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["opposed", "0", "60"])

    def test_opposed_command_rejects_non_positive_batch_size(self) -> None:
        """The opposed command rejects non-positive batch sizes."""
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["opposed", "40", "60", "--batch-size", "0"])

    def test_opposed_command_rejects_non_positive_precision(self) -> None:
        """The opposed command rejects non-positive precision values."""
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["opposed", "40", "60", "--precision", "0"])

    def test_build_runner_config_uses_shared_options(self) -> None:
        """Runner configuration is built from shared CLI options."""
        parser = build_parser()
        args = parser.parse_args(
            [
                "opposed",
                "40",
                "60",
                "--batch-size",
                "500",
                "--precision",
                "0.01",
                "--seed",
                "123",
            ]
        )

        config = build_runner_config(args)

        self.assertEqual(config.batch_size, 500)
        self.assertEqual(config.sensitivity, 0.01)
        self.assertEqual(config.seed, 123)


class CliMainTest(unittest.TestCase):
    """Test command-line execution."""

    @patch("builtins.print")
    @patch("myst_calculator.cli.app.Runner")
    def test_main_runs_opposed_command(
        self,
        runner_class: Mock,
        print_mock: Mock,
    ) -> None:
        """The opposed command runs through the configured runner."""
        stats = Mock(mean=1.5, sample_std=0.25)
        runner = Mock()
        runner.run.return_value = stats
        runner_class.return_value = runner

        result = main(
            [
                "opposed",
                "40",
                "60",
                "--batch-size",
                "500",
                "--precision",
                "0.01",
                "--seed",
                "123",
            ]
        )

        self.assertEqual(result, 0)
        config = runner_class.call_args.kwargs["config"]
        self.assertEqual(config.batch_size, 500)
        self.assertEqual(config.sensitivity, 0.01)
        self.assertEqual(config.seed, 123)
        runner.run.assert_called_once_with()
        print_mock.assert_any_call("mean=1.5")
        print_mock.assert_any_call("std=0.25")


if __name__ == "__main__":
    unittest.main()
