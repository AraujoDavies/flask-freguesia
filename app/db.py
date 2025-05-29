import logging
from datetime import date
from enum import Enum as PyEnum

from sqlalchemy import Enum, String, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

logging.basicConfig(
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(levelname)s: %(message)s",
)


engine = create_engine("sqlite:///freguesia.db", echo=False)


class Base(DeclarativeBase):
    pass


class FreguesEnum(PyEnum):
    mandante = "mandante"
    visitante = "visitante"


class ResultadoEnum(PyEnum):
    green = "green"
    red = "red"


class PadraoFreguesia(Base):
    __tablename__ = "tbl_padrao_freguesia"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_partida: Mapped[date] = mapped_column(nullable=True)
    campeonato: Mapped[str] = mapped_column(String(145))
    mandante: Mapped[str] = mapped_column(String(145))
    visitante: Mapped[str] = mapped_column(String(145))
    fregues: Mapped[FreguesEnum] = mapped_column(Enum(FreguesEnum), nullable=False)
    placar: Mapped[str] = mapped_column(String(45), nullable=True)

    odd_mandante: Mapped[float] = mapped_column(nullable=True)
    odd_visitante: Mapped[float] = mapped_column(nullable=True)
    resultado: Mapped[ResultadoEnum] = mapped_column(Enum(ResultadoEnum), nullable=True)

    url: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"Jogos(id={self.id!r}, url={self.url!r})"


if __name__ == "__main__":
    logging.info("Rodando script de criação do banco...")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        spfc = PadraoFreguesia(
            data_partida=date(2025, 5, 24),
            url="https://www.academiadasapostasbrasil.com/stats/match/brasil/brasileirao-serie-a/sao-paulo/mirassol/l2OZXd0rRZ7Wb",
            fregues="visitante",
            campeonato="brasil/brasileirao-serie-a",
            mandante="sao-paulo",
            visitante="mirassol",
        )

        session.add_all([spfc])
        try:
            session.commit()
            logging.info("Banco criado com sucesso!")
        except IntegrityError:
            logging.warning("Banco não foi criado pois já existe")


    # with Session(engine) as session:
    #     session.