"""Configuration helpers for the recommendation pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import dotenv

# Load environment variables once per process. This mirrors how Google/Meta projects
# centralize configuration loading instead of scattering `dotenv.load_dotenv()` in
# multiple modules.
dotenv.load_dotenv()


@dataclass(frozen=True)
class DatabaseConfig:
    """Connection parameters for PostgreSQL."""

    host: str
    database: str = "postgres"
    user: str = "postgres"
    password: str = ""

    @property
    def sqlalchemy_url(self) -> str:
        """Return the SQLAlchemy-compatible connection string."""
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}/{self.database}"
        )


def load_database_config() -> DatabaseConfig:
    """Instantiate the DB config from environment variables."""
    host = os.getenv("IP")
    password = os.getenv("PASSWORD", "")
    if not host or not password:
        raise RuntimeError("Both IP and PASSWORD environment variables must be set.")
    return DatabaseConfig(host=host, password=password)


def imdb_movies_path() -> Path:
    """Return the canonical location of the parquet file with IMDb metadata."""
    return Path("aws") / "imdb_movies.parquet"


def output_predictions_path() -> Path:
    """Return the path used to export recommendations for sharing/downstream ETL."""
    return Path("aws") / "imdb_model_infer.parquet"


DEFAULT_TABLE_NAME = "model_infer"
DEFAULT_SCHEMA = "imdb_alv"

