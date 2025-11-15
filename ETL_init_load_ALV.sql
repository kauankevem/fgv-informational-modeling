WITH src AS (SELECT DISTINCT email, telefone FROM oper_alv.usuario),
m AS (SELECT ROW_NUMBER() OVER (ORDER BY email, telefone) AS usuariosk, email, telefone FROM src)
INSERT INTO dw_alv.usuario(usuariosk, email, telefone)
SELECT usuariosk, email, telefone FROM m;

WITH src AS (SELECT DISTINCT bairro, municipio, estado, logradouro FROM oper_alv.usuario),
m AS (SELECT ROW_NUMBER() OVER (ORDER BY bairro,municipio,estado,logradouro) AS enderecosk, bairro,municipio,estado,logradouro FROM src)
INSERT INTO dw_alv.endereco(enderecosk,bairro,municipio,estado,logradouro)
SELECT enderecosk,bairro,municipio,estado,logradouro FROM m;

DROP TABLE IF EXISTS temp_map_usuario;
CREATE TEMP TABLE temp_map_usuario AS
SELECT u.usuarioid, d.usuariosk
FROM oper_alv.usuario u
JOIN dw_alv.usuario d ON d.email=u.email AND d.telefone=u.telefone;

DROP TABLE IF EXISTS temp_map_endereco;
CREATE TEMP TABLE temp_map_endereco AS
SELECT enderecosk,bairro,municipio,estado,logradouro FROM dw_alv.endereco;

DROP TABLE IF EXISTS temp_map_filme;
CREATE TEMP TABLE temp_map_filme AS
SELECT filmeid, ROW_NUMBER() OVER (ORDER BY filmeid) AS filmesk
FROM oper_alv.filme;

INSERT INTO dw_alv.filme(filmesk,duracaomin,filmenome,anodelancamento,generonome)
SELECT m.filmesk, f.duracaomin, f.filmenome, f.anode_lancamento,
       -- CORREÇÃO: Adicionado COALESCE para tratar filmes sem gênero e evitar o erro de NOT NULL.
       COALESCE(fg.generofilme, 'Gênero Desconhecido')
FROM oper_alv.filme f
JOIN temp_map_filme m USING (filmeid)
LEFT JOIN (
    SELECT filmeid, MIN(generofilme) AS generofilme
    FROM oper_alv.filme_generofilme
    GROUP BY filmeid
) fg USING (filmeid);

-- CORREÇÃO: Removido o bloco que criava a tabela temp_map_genero, pois a tabela dw_alv.generofilme não existe.
-- CREATE TEMP TABLE temp_map_genero AS ...

DROP TABLE IF EXISTS temp_map_produtora;
CREATE TEMP TABLE temp_map_produtora AS
SELECT produtoraid, ROW_NUMBER() OVER (ORDER BY produtoraid) AS produtorask
FROM oper_alv.produtora;

INSERT INTO dw_alv.produtora(produtorask,produtoranome)
SELECT m.produtorask, p.produtoranome
FROM oper_alv.produtora p
JOIN temp_map_produtora m USING (produtoraid);

INSERT INTO dw_alv.produtora(produtorask,produtoranome)
SELECT COALESCE((SELECT MAX(produtorask)+1 FROM dw_alv.produtora),1), 'Produtora Desconhecida'
WHERE NOT EXISTS (SELECT 1 FROM dw_alv.produtora WHERE produtoranome='Produtora Desconhecida');

DROP TABLE IF EXISTS temp_unknown_produtora;
CREATE TEMP TABLE temp_unknown_produtora AS
SELECT produtorask FROM dw_alv.produtora WHERE produtoranome='Produtora Desconhecida' LIMIT 1;

WITH limites AS (
  SELECT
    LEAST(COALESCE((SELECT MIN(avaliacaodata) FROM oper_alv.avaliacao), CURRENT_DATE),
          COALESCE((SELECT MIN(datapagto) FROM oper_alv.usrpagto), CURRENT_DATE)) AS min_d,
    GREATEST(COALESCE((SELECT MAX(avaliacaodata) FROM oper_alv.avaliacao), CURRENT_DATE),
             COALESCE((SELECT MAX(datapagto) FROM oper_alv.usrpagto), CURRENT_DATE)) AS max_d
),
series AS (SELECT generate_series(min_d, max_d, interval '1 day')::date AS d FROM limites),
rot AS (
  SELECT ROW_NUMBER() OVER (ORDER BY d) AS calendariosk,
         d AS datacompleta, TO_CHAR(d,'Dy') AS diasemana,
         EXTRACT(DAY FROM d)::int AS dia, EXTRACT(MONTH FROM d)::int AS mes,
         EXTRACT(QUARTER FROM d)::int AS trimestre, EXTRACT(YEAR FROM d)::int AS ano
  FROM series
)
INSERT INTO dw_alv.calendario(calendariosk,datacompleta,diasemana,dia,mes,trimestre,ano)
SELECT calendariosk,datacompleta,diasemana,dia,mes,trimestre,ano FROM rot;

DROP TABLE IF EXISTS temp_map_cal;
CREATE TEMP TABLE temp_map_cal AS
SELECT datacompleta, calendariosk FROM dw_alv.calendario;

DROP TABLE IF EXISTS temp_gen_principal;
CREATE TEMP TABLE temp_gen_principal AS
SELECT filmeid, MIN(generofilme) AS generoprincipal
FROM oper_alv.filme_generofilme
GROUP BY filmeid;

DROP TABLE IF EXISTS temp_produtora_filme;
CREATE TEMP TABLE temp_produtora_filme AS
SELECT filmeid, (ARRAY_AGG(produtoraid ORDER BY datapagto DESC))[1] AS produtoraid
FROM oper_alv.filmpagtoroy
GROUP BY filmeid;

-- Usar AvaliacaoID como avaliacaoSK (não mais serial)
INSERT INTO dw_alv.avaliacao(avaliacaoSK, nota, usuariosk, filmesk, produtorask, calendariosk)
SELECT
  a.avaliacaoid,
  a.nota,
  mu.usuariosk,
  mf.filmesk,
  COALESCE(mp.produtorask, up.produtorask),
  mc.calendariosk
FROM oper_alv.avaliacao a
JOIN temp_map_usuario mu ON mu.usuarioid = a.usuarioid
JOIN temp_map_filme   mf ON mf.filmeid   = a.filmeid
LEFT JOIN temp_produtora_filme pf ON pf.filmeid = a.filmeid
LEFT JOIN temp_map_produtora mp   ON mp.produtoraid = pf.produtoraid
CROSS JOIN temp_unknown_produtora up
JOIN temp_map_cal mc ON mc.datacompleta = a.avaliacaodata;

-- CORREÇÃO: A coluna ReceitaID não é mais inserida, pois agora é SERIAL (autoincremental).
INSERT INTO dw_alv.receita(receitask, valorpago, usuariosk, calendariosk, enderecosk)
SELECT
  upg.usrpagtoid,
  upg.valorpago,
  mu.usuariosk,
  mc.calendariosk,
  me.enderecosk
FROM oper_alv.usrpagto upg
JOIN oper_alv.usuario u ON u.usuarioid = upg.usuarioid
JOIN temp_map_usuario mu ON mu.usuarioid = u.usuarioid
JOIN temp_map_cal mc ON mc.datacompleta = upg.datapagto
JOIN temp_map_endereco me
  ON me.bairro=u.bairro AND me.municipio=u.municipio AND me.estado=u.estado AND me.logradouro=u.logradouro;