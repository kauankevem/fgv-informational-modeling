-- Remover qualquer referência de endereço diretamente na dimensão de usuário.
ALTER TABLE dw_alv.usuario DROP COLUMN IF EXISTS enderecosk;
ALTER TABLE dw_alv.avaliacao DROP COLUMN IF EXISTS enderecosk;

-- Reatribuir os endereços para ficar apenas um registro por estado.
DROP TABLE IF EXISTS map_endereco;
CREATE TEMP TABLE map_endereco AS
SELECT
    old.EnderecoSK AS EnderecoSK_original,
    old.Estado,
    new.EnderecoSK AS EnderecoSK_new
FROM dw_alv.Endereco old
LEFT JOIN (
    SELECT DISTINCT ON (Estado)
        EnderecoSK,
        Estado
    FROM dw_alv.Endereco
    ORDER BY Estado, EnderecoSK
) new
    ON old.Estado = new.Estado;

UPDATE dw_alv.receita r
SET EnderecoSK = m.EnderecoSK_new
FROM map_endereco m
WHERE r.EnderecoSK = m.EnderecoSK_original;

-- Manter apenas um endereço por estado.
DELETE FROM dw_alv.endereco a
USING (
    SELECT MIN(EnderecoSK) AS keep_id, Estado
    FROM dw_alv.endereco
    GROUP BY Estado
) b
WHERE a.EnderecoSK <> b.keep_id
  AND a.Estado = b.Estado;

ALTER TABLE dw_alv.endereco
DROP COLUMN IF EXISTS bairro,
DROP COLUMN IF EXISTS logradouro,
DROP COLUMN IF EXISTS municipio;

-- Garantir que a dimensão de filmes possua um indicador de catálogo.
ALTER TABLE dw_alv.filme
    ADD COLUMN IF NOT EXISTS EmCatalogo BOOLEAN NOT NULL DEFAULT TRUE;

-- Inserir filmes do IMDb como registros "fora do catálogo".
DROP TABLE IF EXISTS temp_imdb_movies;
CREATE TEMP TABLE temp_imdb_movies AS
SELECT DISTINCT
    mi."FilmeNome",
    mi."AnoDeLancamento",
    mi."DuracaoMin",
    mi."GeneroNome"
FROM imdb_alv.model_infer mi;

WITH existing AS (
    SELECT FilmeSK, FilmeNome, AnoDeLancamento, DuracaoMin
    FROM dw_alv.filme
),
to_insert AS (
    SELECT
        t."FilmeNome",
        t."AnoDeLancamento",
        t."DuracaoMin",
        t."GeneroNome",
        ROW_NUMBER() OVER (ORDER BY t."FilmeNome", t."AnoDeLancamento", t."DuracaoMin") AS rn
    FROM temp_imdb_movies t
    LEFT JOIN existing e
        ON LOWER(e.FilmeNome) = LOWER(t."FilmeNome")
       AND e.AnoDeLancamento = t."AnoDeLancamento"
       AND e.DuracaoMin = t."DuracaoMin"
    WHERE e.FilmeSK IS NULL
),
max_key AS (
    SELECT COALESCE(MAX(FilmeSK), 0) AS max_id FROM dw_alv.filme
)
INSERT INTO dw_alv.filme(FilmeSK, DuracaoMin, FilmeNome, AnoDeLancamento, GeneroNome, EmCatalogo)
SELECT
    max_key.max_id + t.rn,
    t."DuracaoMin",
    t."FilmeNome",
    t."AnoDeLancamento",
    t."GeneroNome",
    FALSE
FROM to_insert t
CROSS JOIN max_key;

-- Estrutura da nova tabela de fato com chave calendária.
CREATE TABLE IF NOT EXISTS dw_alv.ModelPrediction
(
    FilmeSK INT NOT NULL REFERENCES dw_alv.Filme(FilmeSK),
    CalendarioSK INT NOT NULL REFERENCES dw_alv.Calendario(CalendarioSK),
    EnderecoSK INT NOT NULL REFERENCES dw_alv.Endereco(EnderecoSK),
    IMDbAvaliacao FLOAT NOT NULL,
    IMDbNumVotos FLOAT NOT NULL,
    PredicaoModelo FLOAT NOT NULL,
    PRIMARY KEY (FilmeSK, CalendarioSK, EnderecoSK)
);

-- Limpa previsões anteriores do mesmo período (caso o processo seja reexecutado).
WITH run_dates AS (
    SELECT DISTINCT mi."DataReferencia"::date AS datareferencia
    FROM imdb_alv.model_infer mi
),
target_calendars AS (
    SELECT c.CalendarioSK
    FROM run_dates rd
    JOIN dw_alv.Calendario c ON c.DataCompleta = rd.datareferencia
)
DELETE FROM dw_alv.ModelPrediction
WHERE CalendarioSK IN (SELECT CalendarioSK FROM target_calendars);

-- Popular a fato consolidando as dimensões.
INSERT INTO dw_alv.ModelPrediction (
    FilmeSK,
    CalendarioSK,
    EnderecoSK,
    IMDbAvaliacao,
    IMDbNumVotos,
    PredicaoModelo
)
SELECT
    f.FilmeSK,
    c.CalendarioSK,
    e.EnderecoSK,
    mi."IMDbAvaliacao",
    mi."IMDbNumVotos",
    mi."PredicaoModelo"
FROM imdb_alv.model_infer mi
JOIN dw_alv.Filme f
    ON LOWER(f.FilmeNome) = LOWER(mi."FilmeNome")
   AND f.AnoDeLancamento = mi."AnoDeLancamento"
   AND f.DuracaoMin = mi."DuracaoMin"
JOIN dw_alv.Endereco e
    ON mi."Estado" = e.Estado
JOIN dw_alv.Calendario c
    ON c.DataCompleta = mi."DataReferencia"::date;
