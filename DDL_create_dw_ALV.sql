CREATE SCHEMA IF NOT EXISTS dw_alv;
SET search_path=dw_alv;

CREATE TABLE Usuario
(
  UsuarioSK INT NOT NULL,
  Email varchar(128) NOT NULL,
  Telefone varchar(64) NOT NULL,
  PRIMARY KEY (UsuarioSK)
);

CREATE TABLE Filme
(
  FilmeSK INT NOT NULL,
  DuracaoMin INT NOT NULL,
  FilmeNome varchar(128) NOT NULL,
  AnoDeLancamento INT NOT NULL,
  GeneroNome VARCHAR(128) NOT NULL,
  PRIMARY KEY (FilmeSK)
);

CREATE TABLE Endereco
(
  EnderecoSK INT NOT NULL,
  Bairro varchar(128) NOT NULL,
  Municipio varchar(128) NOT NULL,
  Estado varchar(64) NOT NULL,
  Logradouro varchar(128) NOT NULL,
  PRIMARY KEY (EnderecoSK)
);

CREATE TABLE Calendario
(
  CalendarioSK INT NOT NULL,
  DataCompleta DATE NOT NULL,
  DiaSemana varchar(9) NOT NULL,
  Dia INT NOT NULL,
  Mes INT NOT NULL,
  Trimestre INT NOT NULL,
  Ano INT NOT NULL,
  PRIMARY KEY (CalendarioSK)
);

CREATE TABLE Produtora
(
  ProdutoraSK INT NOT NULL,
  ProdutoraNome varchar(128) NOT NULL,
  PRIMARY KEY (ProdutoraSK)
);

CREATE TABLE Avaliacao
(
  AvaliacaoSK INT NOT NULL,
  Nota INT NOT NULL,
  UsuarioSK INT NOT NULL,
  FilmeSK INT NOT NULL,
  ProdutoraSK INT NOT NULL,
  CalendarioSK INT NOT NULL,
  PRIMARY KEY (AvaliacaoSK),
  FOREIGN KEY (UsuarioSK) REFERENCES Usuario(UsuarioSK),
  FOREIGN KEY (FilmeSK) REFERENCES Filme(FilmeSK),
  FOREIGN KEY (ProdutoraSK) REFERENCES Produtora(ProdutoraSK),
  FOREIGN KEY (CalendarioSK) REFERENCES Calendario(CalendarioSK)
);

CREATE TABLE Receita
(
  ReceitaSK INT NOT NULL,
  ValorPago FLOAT NOT NULL,
  UsuarioSK INT NOT NULL,
  CalendarioSK INT NOT NULL,
  EnderecoSK INT NOT NULL,
  PRIMARY KEY (ReceitaSK),
  FOREIGN KEY (UsuarioSK) REFERENCES Usuario(UsuarioSK),
  FOREIGN KEY (CalendarioSK) REFERENCES Calendario(CalendarioSK),
  FOREIGN KEY (EnderecoSK) REFERENCES Endereco(EnderecoSK)
);