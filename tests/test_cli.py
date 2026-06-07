"""Tests for the command-line interface."""

import argparse
import contextlib
import io
import os
import unittest
from unittest.mock import Mock, patch

from myst_calculator.cli.app import (
    ResultRenderer,
    BUCKET_LINE_WIDTH,
    build_parser,
    build_runner_config,
    format_results,
    main,
    parse_positive_float,
    parse_positive_int,
    parse_roll_type,
    precision_decimal_places,
    terminal_width,
)
from myst_calculator.core.roll import RollType
from myst_calculator.core.runner import RunnerConfig
from myst_calculator.core.stats import RunningStats


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
        self.assertEqual(args.bucket_start, RunnerConfig.bucket_start)
        self.assertEqual(args.bucket_step, RunnerConfig.bucket_step)

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

    def test_attack_command_accepts_all_sampler_parameters(self) -> None:
        """The attack command exposes every attack sampler parameter."""
        parser = build_parser()

        args = parser.parse_args(
            [
                "attack",
                "70",
                "55",
                "8",
                "-1",
                "3",
                "--attack-roll-type",
                "ADVANTAGE",
                "--defense-roll-type",
                "DISADVANTAGE",
            ]
        )

        self.assertEqual(args.attack, 70)
        self.assertEqual(args.defense, 55)
        self.assertEqual(args.dice, 8)
        self.assertEqual(args.dice_bonus, -1)
        self.assertEqual(args.flat_dmg, 3)
        self.assertEqual(args.attack_roll_type, RollType.ADVANTAGE)
        self.assertEqual(args.defense_roll_type, RollType.DISADVANTAGE)

    def test_attack_command_defaults_roll_types_to_normal(self) -> None:
        """The attack command defaults both roll types to normal."""
        parser = build_parser()

        args = parser.parse_args(["attack", "70", "55", "8", "1", "3"])

        self.assertEqual(args.attack_roll_type, RollType.NORMAL)
        self.assertEqual(args.defense_roll_type, RollType.NORMAL)

    def test_attack_command_rejects_non_positive_die_size(self) -> None:
        """The attack command requires a positive damage die size."""
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["attack", "70", "55", "0", "1", "3"])

    def test_opposed_command_accepts_shared_runner_options(self) -> None:
        """Runner options are accepted after the subcommand."""
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
                "--bucket-start",
                "0.5",
                "--bucket-step",
                "2",
            ]
        )

        self.assertEqual(args.batch_size, 500)
        self.assertEqual(args.precision, 0.01)
        self.assertEqual(args.seed, 123)
        self.assertEqual(args.bucket_start, 0.5)
        self.assertEqual(args.bucket_step, 2.0)

    def test_opposed_command_accepts_runner_options_before_subcommand(self) -> None:
        """Runner options are accepted before the subcommand."""
        parser = build_parser()

        args = parser.parse_args(
            [
                "--batch-size",
                "500",
                "--precision",
                "0.01",
                "--seed",
                "123",
                "--bucket-start",
                "0.5",
                "--bucket-step",
                "2",
                "opposed",
                "40",
                "60",
            ]
        )

        self.assertEqual(args.batch_size, 500)
        self.assertEqual(args.precision, 0.01)
        self.assertEqual(args.seed, 123)
        self.assertEqual(args.bucket_start, 0.5)
        self.assertEqual(args.bucket_step, 2.0)

    def test_runner_options_after_subcommand_override_global_values(self) -> None:
        """Subcommand runner options override values provided globally."""
        parser = build_parser()

        args = parser.parse_args(
            [
                "--batch-size",
                "500",
                "--precision",
                "0.01",
                "opposed",
                "40",
                "60",
                "--batch-size",
                "250",
                "--precision",
                "0.1",
            ]
        )

        self.assertEqual(args.batch_size, 250)
        self.assertEqual(args.precision, 0.1)

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

    def test_opposed_command_rejects_non_positive_bucket_step(self) -> None:
        """The opposed command rejects non-positive bucket widths."""
        parser = build_parser()

        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["opposed", "40", "60", "--bucket-step", "0"])

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
                "--bucket-start",
                "0.5",
                "--bucket-step",
                "2",
            ]
        )

        config = build_runner_config(args)

        self.assertEqual(config.batch_size, 500)
        self.assertEqual(config.sensitivity, 0.01)
        self.assertEqual(config.seed, 123)
        self.assertEqual(config.bucket_start, 0.5)
        self.assertEqual(config.bucket_step, 2.0)

    def test_format_results_shows_bucket_contributions(self) -> None:
        """Formatted results include percentages and contribution bars."""
        stats = RunningStats()
        for value in [0.0, 0.0, 1.0, 3.0]:
            stats.add(value)

        lines = format_results(stats)

        self.assertEqual(
            lines[:5],
            (
                "=" * BUCKET_LINE_WIDTH,
                "             0  50.00% |####################                    |",
                "             1  25.00% |##########                              |",
                "             2   0.00% |                                        |",
                "             3  25.00% |##########                              |",
            ),
        )

    def test_precision_decimal_places_uses_precision_resolution(self) -> None:
        """Precision values map to their normalized decimal resolution."""
        self.assertEqual(precision_decimal_places(1.0), 0)
        self.assertEqual(precision_decimal_places(0.01), 2)
        self.assertEqual(precision_decimal_places(0.0001), 4)

    def test_format_results_rounds_stats_to_precision(self) -> None:
        """Mean and standard deviation use the precision's decimal places."""
        stats = RunningStats()
        stats.add(1.25)
        stats.add(1.75)

        lines = format_results(stats, precision=0.01)

        self.assertEqual(
            lines[-4:],
            (
                "-" * BUCKET_LINE_WIDTH,
                "        mean=1.50",
                "        std=0.35",
                "=" * BUCKET_LINE_WIDTH,
            ),
        )

    def test_format_results_uses_requested_frame_width(self) -> None:
        """Separators span the requested width when wider than bucket rows."""
        stats = RunningStats()
        stats.add(0.0)

        lines = format_results(stats, width=100)

        self.assertEqual(lines[0], "=" * 100)
        self.assertEqual(lines[-4], "-" * 100)
        self.assertEqual(lines[-1], "=" * 100)

    def test_format_results_does_not_shrink_below_bucket_width(self) -> None:
        """Separators remain wide enough to contain a complete bucket row."""
        stats = RunningStats()
        stats.add(0.0)

        lines = format_results(stats, width=20)

        self.assertEqual(len(lines[0]), BUCKET_LINE_WIDTH)
        self.assertEqual(len(lines[-4]), BUCKET_LINE_WIDTH)

    @patch("myst_calculator.cli.app.os.get_terminal_size")
    def test_terminal_width_uses_terminal_columns(self, get_size: Mock) -> None:
        """Terminal width uses the stream's current terminal dimensions."""
        stream = Mock()
        stream.fileno.return_value = 7
        get_size.return_value = os.terminal_size((120, 40))

        self.assertEqual(terminal_width(stream), 120)
        get_size.assert_called_once_with(7)

    def test_interactive_renderer_replaces_previous_frame(self) -> None:
        """Interactive updates clear and replace the previously rendered lines."""
        stream = io.StringIO()
        renderer = ResultRenderer(stream, interactive=True, precision=0.01)
        stats = RunningStats()
        stats.add(0.0)

        renderer.update(stats)
        first_frame_line_count = len(format_results(stats, precision=0.01))
        stats.add(1.0)
        renderer.update(stats)

        output = stream.getvalue()
        self.assertIn(f"\x1b[{first_frame_line_count}F", output)
        self.assertEqual(output.count("\x1b[2K"), first_frame_line_count)
        self.assertTrue(
            output.endswith("\n".join(format_results(stats, precision=0.01)) + "\n")
        )

    def test_non_interactive_renderer_writes_only_final_results(self) -> None:
        """Redirected output receives one final frame without terminal controls."""
        stream = io.StringIO()
        renderer = ResultRenderer(stream, interactive=False, precision=0.01)
        stats = RunningStats()
        stats.add(0.0)
        renderer.update(stats)
        stats.add(1.0)
        renderer.update(stats)

        self.assertEqual(stream.getvalue(), "")

        renderer.finish()

        self.assertEqual(
            stream.getvalue(),
            "\n".join(format_results(stats, precision=0.01)) + "\n",
        )


class CliMainTest(unittest.TestCase):
    """Test command-line execution."""

    @patch("myst_calculator.ui.launch", return_value=0)
    def test_main_launches_ui_without_arguments(self, launch: Mock) -> None:
        """An argument-free invocation launches the desktop interface."""
        result = main([])

        self.assertEqual(result, 0)
        launch.assert_called_once_with()

    @patch("myst_calculator.cli.app.sys.stdout", new_callable=io.StringIO)
    @patch("myst_calculator.cli.app.Runner")
    def test_main_runs_opposed_command(
        self,
        runner_class: Mock,
        stdout: io.StringIO,
    ) -> None:
        """The opposed command runs through the configured runner."""
        stats = RunningStats()
        stats.add(1.25)
        stats.add(1.75)
        runner = Mock()

        def run(on_batch: object) -> RunningStats:
            on_batch(stats)
            return stats

        runner.run.side_effect = run
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
                "--bucket-start",
                "0.5",
                "--bucket-step",
                "2",
            ]
        )

        self.assertEqual(result, 0)
        config = runner_class.call_args.kwargs["config"]
        self.assertEqual(config.batch_size, 500)
        self.assertEqual(config.sensitivity, 0.01)
        self.assertEqual(config.seed, 123)
        self.assertEqual(config.bucket_start, 0.5)
        self.assertEqual(config.bucket_step, 2.0)
        runner.run.assert_called_once()
        self.assertIn("        mean=1.50", stdout.getvalue())
        self.assertIn("        std=0.35", stdout.getvalue())

    @patch("myst_calculator.cli.app.sys.stdout", new_callable=io.StringIO)
    @patch("myst_calculator.cli.app.Runner")
    @patch("myst_calculator.cli.app.attack_action_sampler")
    def test_main_runs_attack_command(
        self,
        attack_sampler: Mock,
        runner_class: Mock,
        stdout: io.StringIO,
    ) -> None:
        """The attack command passes every parameter to its sampler."""
        stats = RunningStats()
        stats.add(5.0)
        runner = Mock()

        def run(on_batch: object) -> RunningStats:
            on_batch(stats)
            return stats

        runner.run.side_effect = run
        runner_class.return_value = runner
        sampler = Mock()
        attack_sampler.return_value = sampler

        result = main(
            [
                "attack",
                "70",
                "55",
                "8",
                "-1",
                "3",
                "--attack-type",
                "ADVANTAGE",
                "--defense-type",
                "DISADVANTAGE",
                "--precision",
                "0.1",
            ]
        )

        self.assertEqual(result, 0)
        attack_sampler.assert_called_once_with(
            70,
            55,
            8,
            -1,
            3,
            RollType.ADVANTAGE,
            RollType.DISADVANTAGE,
        )
        runner_class.assert_called_once()
        self.assertIs(runner_class.call_args.args[0], sampler)
        self.assertIn("        mean=5.0", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
