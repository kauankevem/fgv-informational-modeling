import pandas as pd

from src.recommender.config import load_database_config
from src.recommender.database import read_table, build_engine


def save_all_to_excel():
    config = load_database_config()
    engine = build_engine(config)

    tables = [
        "Usuario",
        "Filme",
        "Endereco",
        "Calendario",
        "Produtora",
        "Avaliacao",
        "Receita",
        "ModelPrediction",
    ]

    with pd.ExcelWriter('output.xlsx') as writer:
        for table in tables:
            df = read_table(engine, f"dw_alv.{table}")
            df.to_excel(writer, sheet_name=table, index=False) 


if __name__ == '__main__':
    save_all_to_excel()
