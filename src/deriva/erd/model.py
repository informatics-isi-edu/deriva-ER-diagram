from dataclasses import dataclass

from deriva.core.ermrest_model import Column, Table
from deriva.erd.constants import SYSTEM_COLUMNS


@dataclass
class ERDColumn:
    name: str
    type: str
    nullok: bool
    is_pk: bool
    is_fk: bool
    is_system: bool
    """whether the column is a system column (e.g. RID, RCT, RMT, etc.)"""

    @classmethod
    def from_ermrest(
        cls, ermrest_column: Column, is_pk: bool, is_fk: bool
    ) -> "ERDColumn":
        return cls(
            name=ermrest_column.name,
            type=ermrest_column.type.typename,
            nullok=ermrest_column.nullok,
            is_pk=is_pk,
            is_fk=is_fk,
            is_system=ermrest_column.name in SYSTEM_COLUMNS,
        )


@dataclass
class ERDTable:
    schema: str
    name: str
    kind: str
    """`table` or `view`"""
    columns: list[ERDColumn]
    is_assoc: bool

    @classmethod
    def from_ermrest(cls, ermrest_table: Table) -> "ERDTable":
        pk_cols = {c.name for k in ermrest_table.keys for c in k.unique_columns}
        fk_cols = {
            c.name for fk in ermrest_table.foreign_keys for c in fk.foreign_key_columns
        }
        return cls(
            schema=ermrest_table.schema.name,
            name=ermrest_table.name,
            kind=ermrest_table.kind,
            columns=[
                ERDColumn.from_ermrest(c, c.name in pk_cols, c.name in fk_cols)
                for c in ermrest_table.column_definitions
            ],
            is_assoc=bool(ermrest_table.is_association()),
        )

    @property
    def table_key(self):
        return f"{self.schema}:{self.name}"

    @staticmethod
    def get_table_key(ermrest_table: Table) -> str:
        return f"{ermrest_table.schema.name}:{ermrest_table.name}"


@dataclass
class ERDEdge:
    constraint: str
    from_table: str
    """schema:table"""
    from_columns: list[str]
    to_table: str
    to_columns: list[str]


@dataclass
class ERDGraph:
    host: str
    catalog_id: str
    tables: dict[str, ERDTable]
    """keyed by schema:table"""
    edges: list[ERDEdge]
