import os
import re
from typing import List

import dotenv
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

dotenv.load_dotenv()


# --- Connection Parameters ---
DB_PARAMS = {
    "host": os.getenv("IP"),
    "database": "postgres",
    "user": "postgres",
    "password": os.getenv("PASSWORD"),
}

db_url = (
    f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}"
    f"@{DB_PARAMS['host']}/{DB_PARAMS['database']}"
)

engine = create_engine(db_url)

FEATURE_COLUMNS = ["anodelancamento", "duracaomin", "generonome", "estado"]
NUMERIC_COLUMNS = ["anodelancamento", "duracaomin"]
CATEGORICAL_COLUMNS = ["generonome", "estado"]
TOP_K_PER_STATE = 25


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [col.lower() for col in normalized.columns]
    return normalized


def read_table(table_name: str) -> pd.DataFrame:
    sql_query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(sql_query, engine)
    return normalize_columns(df)


def create_and_populate_table(
    df: pd.DataFrame, table_name: str, schema: str, exists: str = "replace"
) -> None:
    if not re.match(r"^[A-Za-z0-9_]+$", schema):
        raise ValueError(
            "Invalid schema name. Allowed characters: letters, numbers, underscore."
        )
    with engine.begin() as conn:
        conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    df.to_sql(table_name, engine, schema=schema, if_exists=exists, index=False)


def most_frequent(series: pd.Series) -> str | float:
    mode = series.mode()
    if not mode.empty:
        return mode.iloc[0]
    return series.iloc[-1]


def build_training_dataset() -> tuple[pd.DataFrame, List[str]]:
    avaliacao = read_table("dw_alv.avaliacao")
    filmes = read_table("dw_alv.filme")
    receita = read_table("dw_alv.receita")
    endereco = read_table("dw_alv.endereco")

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
                user_state.groupby("usuariosk")["estado"].agg(most_frequent).reset_index()
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


def train_model(training_df: pd.DataFrame) -> Pipeline:
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

    model = Pipeline([("preprocess", preprocessor), ("regressor", regressor)])
    model.fit(training_df[FEATURE_COLUMNS], training_df["nota"])
    return model


def prepare_candidate_movies(limit: int = 400) -> pd.DataFrame:
    df_imdb = pd.read_parquet("aws/imdb_movies.parquet")
    rename_map = {
        "tconst": "FilmeIMDbSKRaw",
        "primarytitle": "FilmeNome",
        "startyear": "AnoDeLancamento",
        "runtimeminutes": "DuracaoMin",
        "genres": "GeneroNome",
        "averagerating": "IMDbAvaliacao",
        "numvotes": "IMDbNumVotos",
    }
    df = df_imdb.rename(columns=rename_map)

    for col in ["AnoDeLancamento", "DuracaoMin", "IMDbAvaliacao", "IMDbNumVotos"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["GeneroNome"] = (
        df["GeneroNome"]
        .fillna("Desconhecido")
        .apply(lambda genres: genres.split(",")[0].strip() if isinstance(genres, str) else "Desconhecido")
    )

    df = df.dropna(subset=["AnoDeLancamento", "DuracaoMin", "IMDbAvaliacao", "IMDbNumVotos"])
    df = df[(df["DuracaoMin"] > 0) & (df["AnoDeLancamento"] > 1900)]
    df = df[(df["IMDbNumVotos"] >= 1000) & (df["IMDbAvaliacao"] >= 6.0)]
    df = df.sort_values(["IMDbAvaliacao", "IMDbNumVotos"], ascending=[False, False])
    return df.head(limit)


def generate_predictions(
    model: Pipeline, base_movies: pd.DataFrame, states: List[str]
) -> pd.DataFrame:
    if not states:
        raise ValueError("Nenhum estado encontrado para gerar previsões.")

    all_predictions = []
    feature_ready = base_movies.copy()
    feature_ready["anodelancamento"] = feature_ready["AnoDeLancamento"].astype(float)
    feature_ready["duracaomin"] = feature_ready["DuracaoMin"].astype(float)
    feature_ready["generonome"] = feature_ready["GeneroNome"]

    for state in states:
        state_frame = feature_ready.copy()
        state_frame["estado"] = state
        preds = model.predict(state_frame[FEATURE_COLUMNS])
        state_frame["PredicaoModelo"] = np.clip(preds, 1.0, 5.0)
        state_frame["Estado"] = state
        all_predictions.append(state_frame)

    combined = pd.concat(all_predictions, ignore_index=True)
    combined = combined.sort_values(["Estado", "PredicaoModelo"], ascending=[True, False])
    combined = combined.groupby("Estado").head(TOP_K_PER_STATE).reset_index(drop=True)

    combined.insert(0, "FilmeIMDbSK", combined.index + 1)

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


def main() -> None:
    training_df, states = build_training_dataset()
    if training_df.empty:
        raise RuntimeError("Não foi possível montar o dataset de treinamento a partir do DW.")

    print(f"Treinando modelo com {len(training_df)} avaliações e {len(states)} estados...")
    model = train_model(training_df)

    candidate_movies = prepare_candidate_movies()
    print(f"Gerando previsões para {len(candidate_movies)} filmes do IMDb...")
    predictions = generate_predictions(model, candidate_movies, states)

    print(f"Gravando {len(predictions)} recomendações no banco...")
    create_and_populate_table(
        predictions,
        table_name="model_infer",
        schema="imdb_alv",
        exists="replace",
    )
    predictions.to_parquet("aws/imdb_model_infer.parquet", index=False)
    print("Arquivo aws/imdb_model_infer.parquet atualizado com sucesso.")


if __name__ == "__main__":
    main()
