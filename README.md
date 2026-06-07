# Myst Calculator

Myst Calculator simulates opposed Myst ability rolls and reports summary
statistics for the result.

## Setup

```sh
mise run sync
```

The project uses `uv` for packaging and dependency management, and `mise` for
local task aliases.

## Desktop UI

Launch the tabbed Tkinter interface by running the command without arguments:

```sh
uv run myst-calculator
```

The Opposed Roll tab exposes scenario, runner, and bucket settings. Simulations
run in the background, update a histogram after each batch, and can be
cancelled. Additional scenarios can be added as notebook tabs.

## CLI

Run an opposed roll simulation:

```sh
uv run myst-calculator opposed 94 76
```

Run an attack action damage simulation:

```sh
uv run myst-calculator attack 70 55 8 1 3 \
  --attack-roll-type ADVANTAGE --defense-roll-type NORMAL
```

The positional attack parameters are `attack`, `defense`, damage die size,
per-die bonus, and flat damage.

Roll type options default to `NORMAL` and accept `NORMAL`, `ADVANTAGE`, or
`DISADVANTAGE`:

```sh
uv run myst-calculator opposed 94 76 --type1 ADVANTAGE --type2 NORMAL
```

Runner and bucket customization options can be provided before or after the
subcommand:

```sh
uv run myst-calculator --batch-size 500 --precision 0.001 --seed 123 \
  --bucket-start 0 --bucket-step 1 opposed 94 76

uv run myst-calculator opposed 94 76 --batch-size 500 --precision 0.001
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
