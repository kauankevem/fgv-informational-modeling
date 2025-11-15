# Trabalho A2

* Apresentação A1: https://www.canva.com/design/DAGz5S2MlUk/JHH_CL4lJ-5hy7bklBqcNA/edit?utm_content=DAGz5S2MlUk&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

## Tutorial

### Conectar no banco de dados PostgreSQL

```bash
sudo -i -u postgres
psql
```

### Banco de dados operacional
Primeiro precisamos criar as tabelas do banco de dados operacional:

```bash
\i DDL_create_tables_ALV.sql;
```

Agora populamos o banco de dados operacional com os dados iniciais:

```bash
\i DML_populate_tables_huge_ALV.sql;
```

Caso queira deletar as tabelas:

```bash
\i DDL_delete_tables_ALV.sql;
```

### Data Warehouse

Primeiro criamos o banco de dados:

```bash
\i DDL_create_dw_ALV.sql;
```

Caso queira deletar as tabelas:

```bash
\i DDL_delete_dw_ALV.sql;
```

Agora basta executar a carga inicial do ETL:

```bash
\i ETL_init_load_ALV.sql;
```

### Dados externos IMDb

Primeiro abra o AWS learner Lab e execute o notebook [external-data-imdb](aws/external-data-imdb.ipynb). Baixe o arquivo `aws/imdb_movies.parquet`.

### Modelo preditivo (Bônus)

Atualmente é o script `mock_model.py`.

Ps: Para rodá-lo é precisso configurar para o python se comunicar com o banco de dados. Veja a seção abaixo.

### ETL incremental

Apenas execute o script:

```bash
\i ETL_incremental_load_ALV.sql;
```

### Extrair dados do Data Warehouse

Não sei

## Conectando com o banco de dados via Python

Não apenas para conectar via python, mas para conseguir conectar at all é preciso abrir permitir acesso à porta 5432 no servidor do banco de dados.

sudo systemctl status postgresql

sudo systemctl start postgresql

sudo ss -tlpn | grep 5432
Problem: If you see 127.0.0.1:5432, it's only listening for local connections.

Correct: You should see 0.0.0.0:5432 (listening on all IPv4 interfaces) or 10.61.49.193:5432 (listening specifically on that interface).

/etc/postgresql/<version>/main/postgresql.conf

* From this:
#listen_addresses = 'localhost'

* To this:
listen_addresses = '*'

sudo systemctl restart postgresql

pg_hba.conf

```bash
```bash
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             10.61.49.0/24           md5
```

sudo systemctl reload postgresql
