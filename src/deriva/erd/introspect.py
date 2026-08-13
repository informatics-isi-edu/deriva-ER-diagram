from collections.abc import Collection

from deriva.core.ermrest_catalog import DerivaServer
from deriva.core.ermrest_model import Table
from deriva.erd.constants import DCCTX, DEFAULT_EXCLUDED_SCHEMAS
from deriva.erd.model import ERDEdge, ERDGraph, ERDTable


def _is_included(schema_name: str, included: frozenset[str] | None) -> bool:
    """An explicit schema list is an allowlist, otherwise fall back to the defaults."""
    if included is not None:
        return schema_name in included
    return schema_name not in DEFAULT_EXCLUDED_SCHEMAS


def _build_edges(ermrest_table: Table, included: frozenset[str] | None) -> list[ERDEdge]:
    edges: list[ERDEdge] = []

    for fk in ermrest_table.foreign_keys:
        if not _is_included(fk.pk_table.schema.name, included):
            continue
        if fk.pk_table.kind != "table":
            continue
        edges.append(
            ERDEdge(
                constraint=fk.constraint_name,
                from_table=ERDTable.get_table_key(ermrest_table),
                from_columns=[c.name for c in fk.foreign_key_columns],
                to_table=ERDTable.get_table_key(fk.pk_table),
                to_columns=[c.name for c in fk.referenced_columns],
            )
        )

    return edges


def get_model(host, catalog_id, credentials):
    server = DerivaServer("https", host, credentials)
    catalog = server.connect_ermrest(catalog_id=catalog_id)
    catalog.dcctx["cid"] = DCCTX

    return catalog.getCatalogModel()


def introspect(
    host: str,
    catalog_id: str,
    credentials,
    schemas: Collection[str] | None = None,
) -> ERDGraph:
    model = get_model(host, credentials=credentials, catalog_id=catalog_id)

    included = frozenset(schemas) if schemas else None
    if included is not None:
        # A typo would otherwise produce an empty diagram with no explanation.
        unknown = included - set(model.schemas)
        if unknown:
            raise ValueError(
                f"unknown schema(s): {', '.join(sorted(unknown))}. "
                f"available: {', '.join(sorted(model.schemas))}"
            )

    tables: dict[str, ERDTable] = {}
    edges: list[ERDEdge] = []
    for ermrest_schema in model.schemas.values():
        if not _is_included(ermrest_schema.name, included):
            continue

        for ermrest_table in ermrest_schema.tables.values():
            table = ERDTable.from_ermrest(ermrest_table)
            if table.kind == "table":
                tables[table.table_key] = table
                edges.extend(_build_edges(ermrest_table, included))

    return ERDGraph(host, catalog_id, tables, edges)
