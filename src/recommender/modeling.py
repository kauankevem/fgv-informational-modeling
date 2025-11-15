"""Model training utilities."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .constants import CATEGORICAL_COLUMNS, FEATURE_COLUMNS, NUMERIC_COLUMNS


def build_model() -> Pipeline:
    """Return an untrained sklearn pipeline for this regression task."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLUMNS),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_COLUMNS,
            ),
        ]
    )
    regressor = RandomForestRegressor(
        n_estimators=300,
        max_depth=12,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline([("preprocess", preprocessor), ("regressor", regressor)])


def train_model(training_df: pd.DataFrame) -> Pipeline:
    """Fit the pipeline using the curated training dataframe."""
    model = build_model()
    model.fit(training_df[FEATURE_COLUMNS], training_df["nota"])
    return model

