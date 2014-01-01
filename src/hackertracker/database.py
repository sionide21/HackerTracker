from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.expression import func


Session = scoped_session(sessionmaker())


class BaseModel(object):
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Model = declarative_base(cls=BaseModel)
