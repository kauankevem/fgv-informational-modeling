-- Cria uma tabela temporária com o EnderecoSK de cada usuário
ALTER TABLE dw_alv.usuario ADD enderecosk INT;
WITH usuario_endereco AS (
    SELECT
        u.usuarioid AS usuariosk,
        e.enderecosk
    FROM oper_alv.usuario u
    LEFT JOIN dw_alv.endereco e
        ON u.bairro = e.bairro
       AND u.municipio = e.municipio
       AND u.estado = e.estado
       AND u.logradouro = e.logradouro
)
UPDATE dw_alv.usuario du
SET enderecosk = ue.enderecosk
FROM usuario_endereco ue
WHERE du.usuariosk = ue.usuariosk;


-- Cria uma tabela temporária para mapear EnderecoSK original para o novo EnderecoSK baseado no Estado
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


-- Atualiza a tabela Receita com o EnderecoSK mais recente baseado no Estado
UPDATE dw_alv.receita r
SET EnderecoSK = m.EnderecoSK_new
FROM map_endereco m
WHERE r.EnderecoSK = m.EnderecoSK_original;


-- Atualiza a tabela Usuario com o EnderecoSK mais recente baseado no Estado
UPDATE dw_alv.usuario u
SET EnderecoSK = m.EnderecoSK_new
FROM map_endereco m
WHERE u.enderecosk = m.EnderecoSK_original;


-- Atualiza a Avaliacao com o EnderecoSK mais recente do usuário
ALTER TABLE dw_alv.avaliacao ADD enderecosk INT;
UPDATE dw_alv.avaliacao a
SET EnderecoSK = u.enderecosk
FROM dw_alv.usuario u
WHERE a.UsuarioSK = u.usuariosk;


-- Deleta a coluna auxiliar ederecosk da tabela Usuario
ALTER TABLE dw_alv.usuario
DROP COLUMN enderecosk;


-- Atualiza a tabela Endereco para conter apenas um registro por Estado
DELETE FROM dw_alv.endereco a
USING (
    SELECT MIN(EnderecoSK) AS keep_id, Estado
    FROM dw_alv.endereco
    GROUP BY Estado
) b
WHERE a.EnderecoSK <> b.keep_id
  AND a.Estado = b.Estado;

ALTER TABLE dw_alv.endereco
DROP COLUMN bairro,
DROP COLUMN logradouro,
DROP COLUMN municipio;


-- Adiciona a nova tabela de fato --
DROP TABLE IF EXISTS dw_alv.ModelPrediction;
CREATE TABLE dw_alv.ModelPrediction
(
    FilmeIMDbSK INT NOT NULL,
    FilmeNome varchar(128) NOT NULL,
    AnoDeLancamento INT NOT NULL,
    DuracaoMin INT NOT NULL,
    GeneroNome varchar(128) NOT NULL,
    IMDbAvaliacao FLOAT NOT NULL,
    IMDbNumVotos FLOAT NOT NULL,
    PredicaoModelo FLOAT NOT NULL,
    EnderecoSK INT NOT NULL,
    PRIMARY KEY (FilmeIMDbSK)
);

INSERT INTO dw_alv.ModelPrediction (FilmeIMDbSK, FilmeNome, AnoDeLancamento, DuracaoMin, GeneroNome, IMDbAvaliacao, IMDbNumVotos, PredicaoModelo, EnderecoSK)
SELECT
    mi."FilmeIMDbSK",
    mi."FilmeNome",
    mi."AnoDeLancamento",
    mi."DuracaoMin",
    mi."GeneroNome",
    mi."IMDbAvaliacao",
    mi."IMDbNumVotos",
    mi."PredicaoModelo",
    e.EnderecoSK
FROM imdb_alv.model_infer mi
LEFT JOIN dw_alv.Endereco e
    ON mi."Estado" = e.Estado;