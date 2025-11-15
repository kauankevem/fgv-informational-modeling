import random
import itertools
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Optional
from abc import ABC, abstractmethod
import faker


def value_wrapper(value: int | str | date) -> str:
    if isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, date):
        return f"'{value}'"
    return str(value)

class TableRow(ABC):
    def __str__(self):
        fields = []
        values = []
        for field, value in self.__dict__.items():
            fields.append(field)
            values.append(value_wrapper(value))
        return f"INSERT INTO {self.__class__.__name__} ({', '.join(fields)}) VALUES ({', '.join(values)});"

@dataclass
class Plano(TableRow):
    PlanoID: int
    PrecoMensal: int
    PlanoNome: str

@dataclass
class Assinatura(TableRow):
    AssinaturaID: int
    DataInicio: date
    DataFim: date
    Status: int
    PlanoID: int

@dataclass
class Usuario(TableRow):
    UsuarioID: int
    Email: str
    Telefone: str
    DataVencimento: date
    CodigoDe_Seguranca: int
    NumeroDo_Cartao: str
    NomeDo_Proprietario: str
    Senha: int
    UsuarioNome: str
    Bairro: str
    Municipio: str
    Estado: str
    Logradouro: str

@dataclass
class Filme(TableRow):
    DuracaoMin: int
    FilmeNome: str
    FilmeID: int
    AnoDe_Lancamento: int

@dataclass
class Avaliacao(TableRow):
    Comentario: Optional[str]
    AvaliacaoData: date
    Nota: int
    AvaliacaoID: int
    UsuarioID: int
    FilmeID: int

@dataclass
class Produtora(TableRow):
    ProdutoraID: int
    ProdutoraNome: str

@dataclass
class Cargo(TableRow):
    CargoID: int
    CargoNome: str

@dataclass
class Funcionario(TableRow):
    FuncionarioID: int
    Salario: float
    FuncionarioNome: str
    CargoID: int

@dataclass
class UsrPagto(TableRow):
    UsrPagtoID: int
    ValorPago: float
    DataPagto: date
    UsuarioID: int
    AssinaturaID: int

@dataclass
class Assiste(TableRow):
    Data: date
    UsuarioID: int
    FilmeID: int

@dataclass
class Modera(TableRow):
    FuncionarioID: int
    AvaliacaoID: int

@dataclass
class Gerencia_Conteudo(TableRow):
    FilmeID: int
    FuncionarioID: int

@dataclass
class FilmPagtoRoy(TableRow):
    ValorPagto: float
    DataPagto: date
    ProdutoraID: int
    FilmeID: int

@dataclass
class Filme_GeneroFilme(TableRow):
    GeneroFilme: str
    FilmeID: int

@dataclass
class Filme_DiretorFilme(TableRow):
    DiretorFilme: str
    FilmeID: int

@dataclass
class Filme_AtorFilme(TableRow):
    AtorFilme: str
    FilmeID: int


class DataBase:
    START_DATE = date(2023, 1, 1)
    END_DATE = date(2025, 12, 31)

    def __init__(self):
        self.tables = defaultdict(list)

    def create_table_plano(self):
        self.tables["Plano"].append(Plano(1, 29, "Básico"))
        self.tables["Plano"].append(Plano(2, 49, "Padrão"))
        self.tables["Plano"].append(Plano(3, 99, "Premium"))

    def create_table_usuario(self, n: int):
        fake = faker.Faker()
        for i in range(1, n + 1):
            self.tables["Usuario"].append(Usuario(
                UsuarioID=i,
                Email=fake.email(),
                Telefone=fake.phone_number(),
                DataVencimento=fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                ),
                CodigoDe_Seguranca=fake.random_int(min=100, max=999),
                NumeroDo_Cartao=fake.credit_card_number(),
                NomeDo_Proprietario=fake.name(),
                Senha=fake.random_int(min=1000, max=9999),
                UsuarioNome=fake.user_name(),
                Bairro=fake.street_name(),
                Municipio=fake.city(),
                Estado=fake.state(),
                Logradouro=fake.street_address()
            ))

    def create_table_filme(self, n: int):
        fake = faker.Faker()
        for i in range(1, n + 1):
            self.tables["Filme"].append(Filme(
                FilmeID=i,
                FilmeNome=fake.word(),
                DuracaoMin=fake.random_int(min=60, max=180),
                AnoDe_Lancamento=fake.year()
            ))

    def create_table_avaliacao(self, n: int):
        fake = faker.Faker()
        pairs = list(itertools.product(self.tables["Usuario"], self.tables["Filme"]))
        pairs = fake.random.sample(pairs, k=min(n, len(pairs)))
        for i, (usuario, filme) in enumerate(pairs):
            self.tables["Avaliacao"].append(Avaliacao(
                AvaliacaoID=i,
                UsuarioID=usuario.UsuarioID,
                FilmeID=filme.FilmeID,
                Nota=fake.random_int(min=1, max=5),
                Comentario=fake.text(),
                AvaliacaoData=fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                )
            ))

    def create_table_produtora(self, n: int):
        fake = faker.Faker()
        for i in range(1, n + 1):
            self.tables["Produtora"].append(Produtora(
                ProdutoraID=i,
                ProdutoraNome=fake.company()
            ))

    def create_table_cargo(self, n: int):
        fake = faker.Faker()
        for i in range(1, n + 1):
            self.tables["Cargo"].append(Cargo(
                CargoID=i,
                CargoNome=fake.job()
            ))

    def create_table_funcionario(self, n: int):
        fake = faker.Faker()
        for i in range(1, n + 1):
            self.tables["Funcionario"].append(Funcionario(
                FuncionarioID=i,
                FuncionarioNome=fake.name(),
                CargoID=fake.random.sample(self.tables["Cargo"], k=1)[0].CargoID,
                Salario=round(fake.random_number(digits=5, fix_len=False) + fake.random.random(), 2)
            ))

    def create_table_assinatura(self, n: int):
        fake = faker.Faker()
        for i in range(1, n + 1):
            start_date, end_date = sorted((
                fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                ),
                fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                )
            ))
            self.tables["Assinatura"].append(Assinatura(
                AssinaturaID=i,
                PlanoID=fake.random.sample(self.tables["Plano"], k=1)[0].PlanoID,
                DataInicio=start_date,
                DataFim=end_date,
                Status=fake.random_int(min=0, max=1)
            ))

    def create_table_film_pagto_roy(self, n: int):
        fake = faker.Faker()
        pairs = list(itertools.product(self.tables["Filme"], self.tables["Produtora"]))
        pairs = fake.random.sample(pairs, k=min(n, len(pairs)))
        for i, (filme, produtora) in enumerate(pairs):
            self.tables["FilmPagtoRoy"].append(FilmPagtoRoy(
                FilmeID=filme.FilmeID,
                DataPagto=fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                ),
                ProdutoraID=produtora.ProdutoraID,
                ValorPagto=fake.random_int(min=1, max=100)
            ))

    def create_table_usr_pagto(self, n: int):
        fake = faker.Faker()
        pairs = list(itertools.product(self.tables["Usuario"], self.tables["Assinatura"]))
        pairs = fake.random.sample(pairs, k=min(n, len(pairs)))
        for i, (usuario, assinatura) in enumerate(pairs):
            self.tables["UsrPagto"].append(UsrPagto(
                UsrPagtoID=i,
                UsuarioID=usuario.UsuarioID,
                AssinaturaID=assinatura.AssinaturaID,
                ValorPago=fake.random_int(min=1, max=100),
                DataPagto=fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                )
            ))

    def create_table_assiste(self, n: int):
        fake = faker.Faker()
        pairs = list(itertools.product(self.tables["Usuario"], self.tables["Filme"]))
        pairs = fake.random.sample(pairs, k=min(n, len(pairs)))
        for i, (usuario, filme) in enumerate(pairs):
            self.tables["Assiste"].append(Assiste(
                UsuarioID=usuario.UsuarioID,
                FilmeID=filme.FilmeID,
                Data=fake.date_between_dates(
                    date_start=self.START_DATE,
                    date_end=self.END_DATE
                )
            ))

    def create_table_modera(self, n: int):
        fake = faker.Faker()
        pairs = list(itertools.product(self.tables["Funcionario"], self.tables["Avaliacao"]))
        pairs = fake.random.sample(pairs, k=min(n, len(pairs)))
        for i, (funcionario, avaliacao) in enumerate(pairs):
            self.tables["Modera"].append(Modera(
                FuncionarioID=funcionario.FuncionarioID,
                AvaliacaoID=avaliacao.AvaliacaoID,
            ))

    def create_table_gerencia_conteudo(self, n: int):
        fake = faker.Faker()
        pairs = list(itertools.product(self.tables["Funcionario"], self.tables["Filme"]))
        pairs = fake.random.sample(pairs, k=min(n, len(pairs)))
        for i, (funcionario, filme) in enumerate(pairs):
            self.tables["Gerencia_Conteudo"].append(Gerencia_Conteudo(
                FuncionarioID=funcionario.FuncionarioID,
                FilmeID=filme.FilmeID,
            ))

    def create_table_filme_genero_filme(self, n: int):
        fake = faker.Faker()
        for filme in fake.random.sample(self.tables["Filme"], k=n):
            self.tables["Filme_Genero"].append(Filme_GeneroFilme(
                FilmeID=filme.FilmeID,
                GeneroFilme=fake.word()
            ))

    def create_table_filme_diretor_filme(self, n: int):
        fake = faker.Faker()
        for filme in fake.random.sample(self.tables["Filme"], k=n):
            self.tables["Filme_Diretor"].append(Filme_DiretorFilme(
                FilmeID=filme.FilmeID,
                DiretorFilme=fake.name()
            ))

    def create_table_filme_ator_filme(self, n: int):
        fake = faker.Faker()
        for filme in fake.random.sample(self.tables["Filme"], k=n):
            self.tables["Filme_Ator"].append(Filme_AtorFilme(
                FilmeID=filme.FilmeID,
                AtorFilme=fake.name()
            ))

    def create_tables(self):
        self.create_table_plano()
        self.create_table_usuario(2000)
        self.create_table_filme(500)
        self.create_table_produtora(20)
        self.create_table_cargo(15)
        self.create_table_funcionario(1000)

        self.create_table_assinatura(1500)
        self.create_table_avaliacao(20000)
        self.create_table_film_pagto_roy(400)
        self.create_table_usr_pagto(6000)
        self.create_table_assiste(15000)
        self.create_table_modera(20)
        self.create_table_gerencia_conteudo(50)

        self.create_table_filme_genero_filme(100)
        self.create_table_filme_diretor_filme(100)
        self.create_table_filme_ator_filme(100)

    def write_dml(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            f.write("set search_path=oper_alv;\n\n")
            f.write("-- DML Statements\n\n")
            for table_name, table in self.tables.items():
                f.write(f"-- Table: {table_name}\n")
                for value in table:
                    f.write(str(value) + "\n")
                f.write("\n")


if __name__ == "__main__":
    db = DataBase()
    db.create_tables()
    db.write_dml("DML_populate_tables_huge_ALV.sql")
