"""Command-line application for Myst Calculator."""

import argparse
from collections.abc import Sequence

from myst_calculator.core.ability_roll import RollType
from myst_calculator.core.myst import opposed_roll_sampler
from myst_calculator.core.runner import Runner, RunnerConfig


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
    )


def run_opposed(args: argparse.Namespace) -> int:
    """Run an opposed roll simulation."""
    sampler = opposed_roll_sampler(
        args.ability1,
        args.ability2,
        args.type1,
        args.type2,
    )
    stats = Runner(sampler, config=build_runner_config(args)).run()
    print(f"mean={stats.mean}")
    print(f"std={stats.sample_std}")
    return 0


def build_runner_options_parser() -> argparse.ArgumentParser:
    """Build the shared parser for runner customization options."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--batch-size",
        "--batch_size",
        dest="batch_size",
        type=parse_positive_int,
        default=RunnerConfig.batch_size,
        help="Number of samples to run per batch.",
    )
    parser.add_argument(
        "--precision",
        type=parse_positive_float,
        default=RunnerConfig.sensitivity,
        help="Maximum mean change required to stop the runner.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=RunnerConfig.seed,
        help="Random seed for reproducible simulations.",
    )
    return parser


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(prog="myst-calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    runner_options = build_runner_options_parser()

    opposed_parser = subparsers.add_parser(
        "opposed",
        parents=[runner_options],
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
