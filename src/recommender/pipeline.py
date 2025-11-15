"""High-level orchestration for the movie recommendation workflow."""

from __future__ import annotations

import logging

import pandas as pd

from .config import (
    DEFAULT_SCHEMA,
    DEFAULT_TABLE_NAME,
    imdb_movies_path,
    load_database_config,
    output_predictions_path,
)
from .constants import CANDIDATE_LIMIT
from .database import build_engine, write_table
from .datasets import build_training_dataset, prepare_candidate_movies
from .modeling import train_model
from .predictor import generate_predictions

LOGGER = logging.getLogger(__name__)


def run_pipeline() -> pd.DataFrame:
    """Execute the full training + inference workflow and return the predictions."""
    config = load_database_config()
    engine = build_engine(config)
    LOGGER.info("Carregando dados do DW...")
    training_df, states = build_training_dataset(engine)
    if training_df.empty:
        raise RuntimeError("Não foi possível montar o dataset de treinamento a partir do DW.")

    LOGGER.info("Treinando modelo com %d avaliações e %d estados.", len(training_df), len(states))
    model = train_model(training_df)

    LOGGER.info("Preparando filmes candidatos a partir do dataset IMDb...")
    candidate_movies = prepare_candidate_movies(imdb_movies_path(), CANDIDATE_LIMIT)

    LOGGER.info("Gerando previsões personalizadas por estado...")
    predictions = generate_predictions(model, candidate_movies, states)
    LOGGER.info("Persistindo previsões no schema %s.%s", DEFAULT_SCHEMA, DEFAULT_TABLE_NAME)
    write_table(
        engine,
        predictions,
        schema=DEFAULT_SCHEMA,
        table_name=DEFAULT_TABLE_NAME,
        if_exists="replace",
    )

    output_path = output_predictions_path()
    LOGGER.info("Salvando arquivo parquet em %s", output_path)
    predictions.to_parquet(output_path, index=False)
    return predictions

