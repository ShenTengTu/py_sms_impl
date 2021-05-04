from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    VARCHAR,
    CHAR,
    TIMESTAMP,
    Boolean,
    MetaData,
)
from sqlalchemy.engine.mock import create_mock_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

_BaseORM = declarative_base(name="_BaseORM")


class MemberORM(_BaseORM):
    __tablename__ = "member"
    member_id = Column(Integer, autoincrement=True, primary_key=True)
    user_email = Column(Text, nullable=False, unique=True)
    user_name = Column(VARCHAR(32), nullable=False, unique=True)
    password_hash = Column(CHAR(60), nullable=False)
    rigister_time = Column(TIMESTAMP, nullable=False)
    email_verified = Column(Boolean, default=False)
    # Relationship
    member_profile = relationship(
        "MemberProfileORM", back_populates="member", uselist=False
    )


class MemberProfileORM(_BaseORM):
    __tablename__ = "member_profile"
    member_id = Column(
        Integer, ForeignKey("member.member_id", ondelete="CASCADE"), primary_key=True
    )
    display_name = Column(VARCHAR(64), nullable=False)
    intro = Column(VARCHAR(256))
    avatar_path = Column(Text)
    # Relationship
    member = relationship("MemberORM", back_populates="member_profile")


def orm_metadata() -> MetaData:
    return _BaseORM.metadata


def dump_schema(scheme: str = "postgresql", driver: str = "psycopg2"):
    s = ""
    dialect = None

    def dump(sql, *multiparams, **params):
        nonlocal s
        if hasattr(sql, "if_not_exists"):
            sql.if_not_exists = True
        c = sql.compile(dialect=dialect)
        s += str(c)

    mock_engine = create_mock_engine(f"{scheme}+{driver}://", dump)
    dialect = mock_engine.dialect
    orm_metadata().create_all(mock_engine)
    return s
