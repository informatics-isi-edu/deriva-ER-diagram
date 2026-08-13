# deriva-er-diagram

Generate an ER diagram for an ERMrest catalog.

The catalog model is read over HTTPS with deriva-py, so no database access is
needed. What you get is what your identity is allowed to see.

> Early work in progress. Only table names and their relationships are drawn.
> Columns are not shown yet.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Graphviz, for anything other than `--format dot`

```sh
brew install graphviz          # macOS
sudo dnf install graphviz      # Fedora
sudo apt install graphviz      # Debian/Ubuntu
```

## Install

```sh
uv sync
```

## Usage

```sh
# whole catalog, minus the ermrest system schemas
uv run deriva-erd --host <host> --catalog-id <id> -o erd.pdf

# a single schema
uv run deriva-erd --host <host> --catalog-id <id> --schema isa -o erd.pdf

# several schemas
uv run deriva-erd --host <host> --catalog-id <id> --schema isa,vocab -o erd.pdf
```

`--host` and `--catalog-id` also read from the `DERIVA_HOST` and `CATALOG_ID`
environment variables.

### Options

| Option | Description |
|---|---|
| `--schema` | Comma-separated schemas to include. Defaults to everything except `public`, `_ermrest` and `_acl_admin`. |
| `-o`, `--output` | Output file. Defaults to `erd.pdf`. |
| `--format` | `pdf`, `svg`, `png` or `dot`. `dot` skips rendering. |
| `--layout` | Graphviz engine: `dot`, `neato`, `sfdp`, `fdp`, `circo`, `twopi`. Defaults to `dot`. |

Run `uv run deriva-erd --help` for the rest.

### Comparing layouts

The engine is chosen at render time, so one `.dot` can be re-rendered every way
without regenerating it:

```sh
uv run deriva-erd --host <host> --catalog-id <id> -o erd.dot --format dot
for e in dot neato sfdp fdp; do dot -K$e -Tpdf erd.dot -o erd-$e.pdf; done
```

`dot` suits smaller schemas, `sfdp` scales to hundreds of tables.

## Notes

deriva-py is pinned to git rather than PyPI. Version 1.7.13 moved the Credenza
auth endpoints and is not released yet, so older versions cannot log in. The
`[tool.uv.sources]` block in `pyproject.toml` can be dropped once it ships.
