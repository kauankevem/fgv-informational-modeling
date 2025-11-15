import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
import re
import dotenv
import os

dotenv.load_dotenv()


# --- Connection Parameters ---
DB_PARAMS = {
    "host":     os.getenv("IP"),
    "database": "postgres",
    "user":     "postgres",
    "password": os.getenv("PASSWORD")
}

# 1. Create the database connection URL
db_url = (
    f"postgresql+psycopg2://{DB_PARAMS['user']}:{DB_PARAMS['password']}"
    f"@{DB_PARAMS['host']}/{DB_PARAMS['database']}"
)

engine = create_engine(db_url)

def read_table(table_name):
    sql_query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(sql_query, engine)
    return df

def create_and_populate_table(df: pd.DataFrame, table_name: str, schema: str, exists: str = 'replace'):
    # validate schema name to avoid SQL injection
    if not re.match(r'^[A-Za-z0-9_]+$', schema):
        raise ValueError("Invalid schema name. Allowed characters: letters, numbers, underscore.")
    # create schema if not exists (use exec_driver_sql to run raw SQL string)
    with engine.begin() as conn:
        conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema};")
    # populate table
    df.to_sql(table_name, engine, schema=schema, if_exists=exists, index=False)

dw_endereco = read_table("dw_alv.endereco")

df_imdb = pd.read_parquet('aws/imdb_movies.parquet')

rename_map = {
    'primarytitle': 'FilmeNome',
    'startyear': 'AnoDeLancamento',
    'runtimeminutes': 'DuracaoMin',
    'genres': 'GeneroNome',
    'averagerating': 'IMDbAvaliacao',
    'numvotes': 'IMDbNumVotos',
}

df_model_input = df_imdb.rename(columns=rename_map)[list(rename_map.values())]

df_model_input = df_model_input[
    (df_model_input['IMDbAvaliacao'] >= 8)
    & (df_model_input['IMDbNumVotos'] > 1000)
]

estados = dw_endereco['estado'].unique().tolist()

df_model_output = []
for estado in estados:
    df_temp = df_model_input.copy()
    df_temp['Estado'] = estado
    df_temp['PredicaoModelo'] = np.random.rand(len(df_temp)) * 5  # Simulated model prediction
    df_temp = df_temp[df_temp['PredicaoModelo'] >= 3.0]
    df_model_output.append(df_temp)

df_model_output = pd.concat(df_model_output, ignore_index=True)

create_and_populate_table(df_model_output, table_name="model_infer", schema="imdb_alv", exists='replace')