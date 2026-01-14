import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Date,
    Float,
    Text,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


Base = declarative_base()


class Person(Base):
    __tablename__ = "people"

    id = Column(Integer, primary_key=True)
    person_key = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    country = Column(String, nullable=True)

    observations = relationship("Observation", back_populates="person")


class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False)
    metric_key = Column(String, nullable=False)
    pillar = Column(String, nullable=False)
    source = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    value_num = Column(Float, nullable=True)
    value_text = Column(String, nullable=True)
    unit = Column(String, nullable=False)
    raw_json = Column(Text, nullable=True)

    person = relationship("Person", back_populates="observations")

    __table_args__ = (
        UniqueConstraint(
            "person_id",
            "metric_key",
            "date",
            name="uniq_person_metric_date"
        ),
    )


def get_engine(db_path=None):
    path = db_path or os.getenv("SIGNAL_INDEX_DB", "data/app.db")
    return create_engine(f"sqlite:///{path}", future=True)


def init_db(engine=None):
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    engine = engine or get_engine()
    return sessionmaker(bind=engine, future=True)()
