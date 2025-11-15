CREATE SCHEMA IF NOT EXISTS oper_alv;
SET search_path=oper_alv;

CREATE TABLE Plano
(
  PlanoID INT NOT NULL,
  PrecoMensal FLOAT NOT NULL,
  PlanoNome VARCHAR(128) NOT NULL,
  PRIMARY KEY (PlanoID)
);

CREATE TABLE Assinatura
(
  AssinaturaID INT NOT NULL,
  DataInicio DATE NOT NULL,
  DataFim DATE NOT NULL,
  Status INT NOT NULL,
  PlanoID INT NOT NULL,
  PRIMARY KEY (AssinaturaID),
  FOREIGN KEY (PlanoID) REFERENCES Plano(PlanoID)
);

CREATE TABLE Usuario
(
  UsuarioID INT NOT NULL,
  Email VARCHAR(128) NOT NULL,
  Telefone VARCHAR(128) NOT NULL,
  DataVencimento DATE NOT NULL,
  CodigoDe_Seguranca INT NOT NULL,
  NumeroDo_Cartao VARCHAR(128) NOT NULL,
  NomeDo_Proprietario VARCHAR(128) NOT NULL,
  Senha INT NOT NULL,
  UsuarioNome VARCHAR(128) NOT NULL,
  Bairro VARCHAR(128) NOT NULL,
  Municipio VARCHAR(128) NOT NULL,
  Estado VARCHAR(128) NOT NULL,
  Logradouro VARCHAR(128) NOT NULL,
  PRIMARY KEY (UsuarioID)
);

CREATE TABLE Filme
(
  DuracaoMin INT NOT NULL,
  FilmeNome VARCHAR(128) NOT NULL,
  FilmeID INT NOT NULL,
  AnoDe_Lancamento INT NOT NULL,
  PRIMARY KEY (FilmeID)
);

CREATE TABLE Avaliacao
(
  Comentario VARCHAR(255),
  AvaliacaoData DATE NOT NULL,
  Nota INT NOT NULL,
  AvaliacaoID INT NOT NULL,
  UsuarioID INT NOT NULL,
  FilmeID INT NOT NULL,
  PRIMARY KEY (AvaliacaoID),
  FOREIGN KEY (UsuarioID) REFERENCES Usuario(UsuarioID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID)
);

CREATE TABLE Produtora
(
  ProdutoraID INT NOT NULL,
  ProdutoraNome VARCHAR(128) NOT NULL,
  PRIMARY KEY (ProdutoraID)
);

CREATE TABLE Cargo
(
  CargoID INT NOT NULL,
  CargoNome VARCHAR(128) NOT NULL,
  PRIMARY KEY (CargoID)
);

CREATE TABLE Funcionario
(
  FuncionarioID INT NOT NULL,
  Salario FLOAT NOT NULL,
  FuncionarioNome VARCHAR(128) NOT NULL,
  CargoID INT NOT NULL,
  PRIMARY KEY (FuncionarioID),
  FOREIGN KEY (CargoID) REFERENCES Cargo(CargoID)
);

CREATE TABLE UsrPagto
(
  UsrPagtoID INT NOT NULL,
  ValorPago FLOAT NOT NULL,
  DataPagto DATE NOT NULL,
  UsuarioID INT NOT NULL,
  AssinaturaID INT NOT NULL,
  PRIMARY KEY (UsrPagtoID),
  FOREIGN KEY (UsuarioID) REFERENCES Usuario(UsuarioID),
  FOREIGN KEY (AssinaturaID) REFERENCES Assinatura(AssinaturaID)
);

CREATE TABLE Assiste
(
  Data DATE NOT NULL,
  UsuarioID INT NOT NULL,
  FilmeID INT NOT NULL,
  PRIMARY KEY (UsuarioID, FilmeID),
  FOREIGN KEY (UsuarioID) REFERENCES Usuario(UsuarioID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID)
);

CREATE TABLE Modera
(
  FuncionarioID INT NOT NULL,
  AvaliacaoID INT NOT NULL,
  PRIMARY KEY (FuncionarioID, AvaliacaoID),
  FOREIGN KEY (FuncionarioID) REFERENCES Funcionario(FuncionarioID),
  FOREIGN KEY (AvaliacaoID) REFERENCES Avaliacao(AvaliacaoID)
);

CREATE TABLE Gerencia_Conteudo
(
  FilmeID INT NOT NULL,
  FuncionarioID INT NOT NULL,
  PRIMARY KEY (FilmeID, FuncionarioID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID),
  FOREIGN KEY (FuncionarioID) REFERENCES Funcionario(FuncionarioID)
);

CREATE TABLE FilmPagtoRoy
(
  ValorPagto FLOAT NOT NULL,
  DataPagto DATE NOT NULL,
  ProdutoraID INT NOT NULL,
  FilmeID INT NOT NULL,
  PRIMARY KEY (ProdutoraID, FilmeID),
  FOREIGN KEY (ProdutoraID) REFERENCES Produtora(ProdutoraID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID)
);

CREATE TABLE Filme_GeneroFilme
(
  GeneroFilme VARCHAR(128) NOT NULL,
  FilmeID INT NOT NULL,
  PRIMARY KEY (GeneroFilme, FilmeID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID)
);

CREATE TABLE Filme_DiretorFilme
(
  DiretorFilme VARCHAR(128) NOT NULL,
  FilmeID INT NOT NULL,
  PRIMARY KEY (DiretorFilme, FilmeID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID)
);

CREATE TABLE Filme_AtorFilme
(
  AtorFilme VARCHAR(128) NOT NULL,
  FilmeID INT NOT NULL,
  PRIMARY KEY (AtorFilme, FilmeID),
  FOREIGN KEY (FilmeID) REFERENCES Filme(FilmeID)
);