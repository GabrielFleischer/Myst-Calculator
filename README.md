# Myst Calculator

Myst Calculator simulates opposed Myst ability rolls and reports summary
statistics for the result.

## Setup

```sh
mise run sync
```

The project uses `uv` for packaging and dependency management, and `mise` for
local task aliases.

## CLI

Run an opposed roll simulation:

```sh
uv run myst-calculator opposed 94 76
```

Roll type options default to `NORMAL` and accept `NORMAL`, `ADVANTAGE`, or
`DISADVANTAGE`:

```sh
uv run myst-calculator opposed 94 76 --type1 ADVANTAGE --type2 NORMAL
```

All subcommands accept runner and bucket customization options:

```sh
uv run myst-calculator opposed 94 76 --batch-size 500 --precision 0.001 \
  --seed 123 --bucket-start 0 --bucket-step 1
```

- `--batch-size` / `--batch_size`: samples to run per batch.
- `--precision`: maximum running mean change required before the simulation stops.
- `--seed`: random seed for reproducible simulations.
- `--bucket-start`: boundary from which buckets are calculated (default: `0`).
- `--bucket-step`: width of each bucket (default: `1`).

The command prints each bucket's contribution followed by the running mean and
sample standard deviation. While running in a terminal, the display updates
in place after each batch:

```text
=================================================================
             0  72.50% |#############################           |
             1  20.00% |########                                |
             2   7.50% |###                                     |
-----------------------------------------------------------------
        mean=2.71
        std=2.83
=================================================================
```

Mean and standard deviation are rounded to the decimal resolution of
`--precision`. Separators span the terminal width and are never narrower than
the bucket rows.

## Development

Format source and tests:

```sh
mise run format
```

Run formatting and compile checks:

```sh
mise run check
```

Run the test suite:

```sh
mise run test
```
