"""Data assembly logic for training and inference."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

import pandas as pd

from .constants import FEATURE_COLUMNS
from .database import normalize_columns, read_table


def _most_frequent(series: pd.Series) -> str:
    """Return the most common entry, handling ties deterministically."""
    mode = series.mode()
    if not mode.empty:
        return mode.iloc[0]
    # Fall back to the last observed value if pandas could not compute a mode.
    return series.iloc[-1]


def build_training_dataset(engine, load_from_database: bool=False) -> Tuple[pd.DataFrame, List[str]]:
    """Assemble the supervised dataset (ratings enriched with metadata)."""
    if load_from_database:
        avaliacao = read_table(engine, "dw_alv.avaliacao")
        filmes = read_table(engine, "dw_alv.filme")
        receita = read_table(engine, "dw_alv.receita")
        endereco = read_table(engine, "dw_alv.endereco")
    else:
        avaliacao = pd.read_csv('data/CSVs/avaliacao.csv')
        endereco = pd.read_csv('data/CSVs/endereco.csv')
        filmes = pd.read_csv('data/CSVs/filme.csv')
        receita = pd.read_csv('data/CSVs/receita.csv')

    filmes_subset = filmes[
        ["filmesk", "filmenome", "anodelancamento", "duracaomin", "generonome"]
    ]

    if receita.empty:
        user_state = pd.DataFrame(columns=["usuariosk", "estado"])
    else:
        user_state = (
            receita[["usuariosk", "enderecosk"]]
            .merge(endereco[["enderecosk", "estado"]], on="enderecosk", how="left")
            .dropna(subset=["estado"])
        )
        if user_state.empty:
            user_state = pd.DataFrame(columns=["usuariosk", "estado"])
        else:
            user_state = (
                user_state.groupby("usuariosk")["estado"].agg(_most_frequent).reset_index()
            )

    training = (
        avaliacao[["avaliacaosk", "usuariosk", "filmesk", "nota"]]
        .merge(filmes_subset, on="filmesk", how="left")
        .merge(user_state, on="usuariosk", how="inner")
    )

    for col in ["anodelancamento", "duracaomin", "nota"]:
        training[col] = pd.to_numeric(training[col], errors="coerce")

    training = training.dropna(subset=FEATURE_COLUMNS + ["nota"])
    states = sorted(training["estado"].unique().tolist())
    return training, states


def prepare_candidate_movies(path: Path, limit: int) -> pd.DataFrame:
    """Load/clean the IMDb metadata that feeds the inference step."""
    df_imdb = pd.read_parquet(path)
    rename_map = {
        "tconst": "FilmeIMDbSKRaw",
        "primarytitle": "FilmeNome",
        "startyear": "AnoDeLancamento",
        "runtimeminutes": "DuracaoMin",
        "genres": "GeneroNome",
        "averagerating": "IMDbAvaliacao",
        "numvotes": "IMDbNumVotos",
    }
    df = normalize_columns(df_imdb.rename(columns=rename_map))

    numeric_cols = ["anodelancamento", "duracaomin", "imdbavaliacao", "imdbnumvotos"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    def pick_primary_genre(value) -> str:
        # The raw file stores genres as "genre1,genre2". We keep the leading genre
        # to maintain compatibility with the existing schema while still capturing
        # the user's dominant preference.
        if isinstance(value, str):
            return value.split(",")[0].strip()
        return "desconhecido"

    df["generonome"] = df["generonome"].fillna("desconhecido").apply(pick_primary_genre)

    df = df.dropna(subset=numeric_cols)
    df = df[(df["duracaomin"] > 0) & (df["anodelancamento"] > 1900)]
    df = df[(df["imdbnumvotos"] >= 1000) & (df["imdbavaliacao"] >= 6.0)]
    df = df.sort_values(["imdbavaliacao", "imdbnumvotos"], ascending=[False, False])
    return df.head(limit)

