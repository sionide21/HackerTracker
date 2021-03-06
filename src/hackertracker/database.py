from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker


Session = scoped_session(sessionmaker())


def is_database_bound():
    return Session.session_factory.kw['bind'] is not None


class BaseModel(object):
    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Model = declarative_base(cls=BaseModel)
