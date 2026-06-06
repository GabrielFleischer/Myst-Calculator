"""Command-line application for Myst Calculator."""

import argparse
import os
import sys
from collections.abc import Sequence
from decimal import Decimal
from typing import TextIO

from myst_calculator.core.ability_roll import RollType
from myst_calculator.core.myst import opposed_roll_sampler
from myst_calculator.core.runner import Runner, RunnerConfig
from myst_calculator.core.stats import RunningStats

RESULT_BAR_WIDTH = 40
BUCKET_LINE_WIDTH = 14 + 1 + 7 + 1 + RESULT_BAR_WIDTH + 2
SUMMARY_INDENT = " " * 8


def parse_positive_int(value: str) -> int:
    """Parse a positive integer command-line value."""
    try:
        parsed = int(value)
    except ValueError as exc:
        msg = f"{value!r} is not an integer."
        raise argparse.ArgumentTypeError(msg) from exc

    if parsed <= 0:
        msg = f"{value!r} is not a positive integer."
        raise argparse.ArgumentTypeError(msg)
    return parsed


def parse_positive_float(value: str) -> float:
    """Parse a positive float command-line value."""
    try:
        parsed = float(value)
    except ValueError as exc:
        msg = f"{value!r} is not a number."
        raise argparse.ArgumentTypeError(msg) from exc

    if parsed <= 0:
        msg = f"{value!r} is not a positive number."
        raise argparse.ArgumentTypeError(msg)
    return parsed


def parse_roll_type(value: str) -> RollType:
    """Parse a roll type command-line value."""
    try:
        return RollType[value.upper()]
    except KeyError as exc:
        choices = ", ".join(roll_type.name for roll_type in RollType)
        msg = f"{value!r} is not a valid roll type. Choose one of: {choices}."
        raise argparse.ArgumentTypeError(msg) from exc


def build_runner_config(args: argparse.Namespace) -> RunnerConfig:
    """Build a runner configuration from parsed command-line arguments."""
    return RunnerConfig(
        seed=args.seed,
        batch_size=args.batch_size,
        sensitivity=args.precision,
        bucket_start=args.bucket_start,
        bucket_step=args.bucket_step,
    )


def format_number(value: float) -> str:
    """Format a bucket boundary without unnecessary trailing zeroes."""
    return f"{value:g}"


def precision_decimal_places(precision: float) -> int:
    """Return the decimal places represented by a precision value."""
    exponent = Decimal(str(precision)).normalize().as_tuple().exponent
    return max(0, -exponent)


def terminal_width(stream: TextIO) -> int:
    """Return the stream terminal width or the minimum result width."""
    try:
        columns = os.get_terminal_size(stream.fileno()).columns
    except AttributeError, OSError:
        return BUCKET_LINE_WIDTH
    return max(columns, BUCKET_LINE_WIDTH)


def format_results(
    stats: RunningStats,
    precision: float = RunnerConfig.sensitivity,
    width: int = BUCKET_LINE_WIDTH,
) -> tuple[str, ...]:
    """Format bucket contributions and summary statistics."""
    frame_width = max(width, BUCKET_LINE_WIDTH)
    border = "=" * frame_width
    separator = "-" * frame_width
    lines = [border]
    for bucket in stats.buckets:
        contribution = bucket.count / stats.count
        filled_width = round(contribution * RESULT_BAR_WIDTH)
        bar = "#" * filled_width + " " * (RESULT_BAR_WIDTH - filled_width)
        label = format_number(bucket.lower_bound)
        lines.append(f"{label:>14} {contribution:7.2%} |{bar}|")

    decimal_places = precision_decimal_places(precision)
    lines.append(separator)
    lines.append(f"{SUMMARY_INDENT}mean={stats.mean:.{decimal_places}f}")
    lines.append(f"{SUMMARY_INDENT}std={stats.sample_std:.{decimal_places}f}")
    lines.append(border)
    return tuple(lines)


class ResultRenderer:
    """Render simulation results, redrawing interactive terminal output."""

    def __init__(
        self,
        stream: TextIO,
        interactive: bool,
        precision: float = RunnerConfig.sensitivity,
    ) -> None:
        """Create a renderer for an output stream."""
        self._stream = stream
        self._interactive = interactive
        self._precision = precision
        self._rendered_line_count = 0
        self._latest_stats: RunningStats | None = None

    @classmethod
    def for_stream(cls, stream: TextIO, precision: float) -> "ResultRenderer":
        """Create a renderer suited to the provided output stream."""
        return cls(
            stream=stream,
            interactive=stream.isatty(),
            precision=precision,
        )

    def update(self, stats: RunningStats) -> None:
        """Record results and redraw them when output is interactive."""
        self._latest_stats = stats
        if self._interactive:
            self._render(stats)

    def finish(self) -> None:
        """Write the final results when they were not rendered interactively."""
        if not self._interactive and self._latest_stats is not None:
            self._render(self._latest_stats)

    def _render(self, stats: RunningStats) -> None:
        lines = format_results(
            stats,
            self._precision,
            width=terminal_width(self._stream),
        )
        if self._rendered_line_count:
            self._clear_previous_frame()

        self._stream.write("\n".join(lines))
        self._stream.write("\n")
        self._stream.flush()
        self._rendered_line_count = len(lines)

    def _clear_previous_frame(self) -> None:
        self._stream.write(f"\x1b[{self._rendered_line_count}F")
        for line_index in range(self._rendered_line_count):
            self._stream.write("\x1b[2K")
            if line_index < self._rendered_line_count - 1:
                self._stream.write("\n")

        if self._rendered_line_count > 1:
            self._stream.write(f"\x1b[{self._rendered_line_count - 1}F")


def run_opposed(args: argparse.Namespace) -> int:
    """Run an opposed roll simulation."""
    sampler = opposed_roll_sampler(
        args.ability1,
        args.ability2,
        args.type1,
        args.type2,
    )
    renderer = ResultRenderer.for_stream(sys.stdout, args.precision)
    Runner(sampler, config=build_runner_config(args)).run(on_batch=renderer.update)
    renderer.finish()
    return 0


def build_runner_options_parser(
    suppress_defaults: bool = False,
) -> argparse.ArgumentParser:
    """Build the shared parser for runner customization options."""
    parser = argparse.ArgumentParser(add_help=False)
    default = argparse.SUPPRESS if suppress_defaults else None
    parser.add_argument(
        "--batch-size",
        "--batch_size",
        dest="batch_size",
        type=parse_positive_int,
        default=default if suppress_defaults else RunnerConfig.batch_size,
        help="Number of samples to run per batch.",
    )
    parser.add_argument(
        "--precision",
        type=parse_positive_float,
        default=default if suppress_defaults else RunnerConfig.sensitivity,
        help="Maximum mean change required to stop the runner.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=default if suppress_defaults else RunnerConfig.seed,
        help="Random seed for reproducible simulations.",
    )
    parser.add_argument(
        "--bucket-start",
        type=float,
        default=default if suppress_defaults else RunnerConfig.bucket_start,
        help="Boundary from which result buckets are calculated.",
    )
    parser.add_argument(
        "--bucket-step",
        type=parse_positive_float,
        default=default if suppress_defaults else RunnerConfig.bucket_step,
        help="Width of each result bucket.",
    )
    return parser


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    global_runner_options = build_runner_options_parser()
    parser = argparse.ArgumentParser(
        prog="myst-calculator",
        parents=[global_runner_options],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subcommand_runner_options = build_runner_options_parser(suppress_defaults=True)

    opposed_parser = subparsers.add_parser(
        "opposed",
        parents=[subcommand_runner_options],
        help="Run an opposed ability roll simulation.",
    )
    opposed_parser.add_argument("ability1", type=parse_positive_int)
    opposed_parser.add_argument("ability2", type=parse_positive_int)
    opposed_parser.add_argument(
        "--type1", type=parse_roll_type, default=RollType.NORMAL
    )
    opposed_parser.add_argument(
        "--type2", type=parse_roll_type, default=RollType.NORMAL
    )
    opposed_parser.set_defaults(handler=run_opposed)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line application."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(args)
