"""Database helpers shared across the pipeline."""

from __future__ import annotations

import re
from typing import Final

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import DatabaseConfig

_SCHEMA_REGEX: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_]+$")


def build_engine(config: DatabaseConfig) -> Engine:
    """Create a SQLAlchemy engine using the provided configuration."""
    return create_engine(config.sqlalchemy_url)


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataframe with lower-cased column names."""
    renamed = df.copy()
    renamed.columns = [col.lower() for col in renamed.columns]
    return renamed


def read_table(engine: Engine, table_name: str) -> pd.DataFrame:
    """Fetch an entire table/SQL expression into a Pandas DataFrame."""
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, engine)
    return normalize_columns(df)


def write_table(
    engine: Engine,
    df: pd.DataFrame,
    *,
    schema: str,
    table_name: str,
    if_exists: str = "replace",
) -> None:
    """Persist a dataframe to PostgreSQL with defensive schema validation."""
    if not _SCHEMA_REGEX.match(schema):
        raise ValueError(
            "Invalid schema name. Allowed characters: letters, numbers, underscore."
        )
    with engine.begin() as conn:
        conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    df.to_sql(table_name, engine, schema=schema, if_exists=if_exists, index=False)

