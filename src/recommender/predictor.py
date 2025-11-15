"""Inference helpers for the recommendation model."""

from __future__ import annotations

from typing import List

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from .constants import FEATURE_COLUMNS, TOP_K_PER_STATE


def generate_predictions(
    model: Pipeline,
    base_movies: pd.DataFrame,
    states: List[str],
    top_k_per_state: int = TOP_K_PER_STATE,
) -> pd.DataFrame:
    """Return ranked recommendations for every state."""
    if not states:
        raise ValueError("Nenhum estado encontrado para gerar previsões.")

    all_predictions = []
    feature_ready = base_movies.copy()

    for state in states:
        state_frame = feature_ready.copy()
        state_frame["estado"] = state
        preds = model.predict(state_frame[FEATURE_COLUMNS])
        state_frame["predicaomodelo"] = np.clip(preds, 1.0, 5.0)
        state_frame["estado"] = state
        all_predictions.append(state_frame)

    combined = pd.concat(all_predictions, ignore_index=True)
    combined = combined.sort_values(["estado", "predicaomodelo"], ascending=[True, False])
    combined = combined.groupby("estado").head(top_k_per_state).reset_index(drop=True)

    # Add surrogate key and convert column names back to the DW-friendly format.
    combined.insert(0, "FilmeIMDbSK", combined.index + 1)
    rename_for_output = {
        "filmenome": "FilmeNome",
        "anodelancamento": "AnoDeLancamento",
        "duracaomin": "DuracaoMin",
        "generonome": "GeneroNome",
        "imdbavaliacao": "IMDbAvaliacao",
        "imdbnumvotos": "IMDbNumVotos",
        "estado": "Estado",
        "predicaomodelo": "PredicaoModelo",
    }
    combined = combined.rename(columns=rename_for_output)

    final_columns = [
        "FilmeIMDbSK",
        "FilmeNome",
        "AnoDeLancamento",
        "DuracaoMin",
        "GeneroNome",
        "IMDbAvaliacao",
        "IMDbNumVotos",
        "Estado",
        "PredicaoModelo",
    ]
    return combined[final_columns]

