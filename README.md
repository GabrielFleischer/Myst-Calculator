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

The command prints the running mean and sample standard deviation:

```text
mean=...
std=...
```

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
