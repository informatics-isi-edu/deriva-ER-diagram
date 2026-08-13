from deriva.erd.model import ERDGraph


def _escape(value: str) -> str:
    """Make text safe to sit inside a quoted DOT string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _header(layout: str) -> list[str]:
    lines = [
        "digraph erd {",
        '  graph [fontname="Helvetica" pad=0.4];',
        '  node [shape=box style="rounded,filled" fillcolor="#38618c"'
        ' fontcolor="white" fontname="Helvetica" fontsize=11];',
        '  edge [color="#555555"];',
    ]
    # rankdir/ranksep only apply to dot, overlap only to the force engines.
    # Setting the wrong ones is silently ignored, which makes tuning confusing.
    if layout == "dot":
        lines += ["  rankdir=LR;", "  ranksep=1.1;", "  nodesep=0.4;"]
    else:
        lines += ["  overlap=prism;", '  sep="+12";']
    return lines


def emit(graph: ERDGraph, layout: str = "dot") -> str:
    """Render the graph as DOT, tables only. Columns are not drawn."""
    lines = _header(layout)
    lines.append("")

    for table in sorted(graph.tables.values(), key=lambda t: t.table_key):
        node = _escape(table.table_key)
        lines.append(f'  "{node}" [label="{_escape(table.name)}"];')

    lines.append("")

    # Without columns there is nothing to distinguish two fkeys between the same
    # pair of tables, so they collapse into a single line.
    for src, dst in sorted({(e.from_table, e.to_table) for e in graph.edges}):
        lines.append(
            f'  "{_escape(src)}" -> "{_escape(dst)}"'
            " [dir=both arrowtail=crow arrowhead=tee];"
        )

    lines.append("}")
    return "\n".join(lines) + "\n"
