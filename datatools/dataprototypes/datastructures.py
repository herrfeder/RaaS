from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base

ORMBase = declarative_base()
meta = MetaData()


class URLInputTable(ORMBase):
    __tablename__ = "url_input_table"
    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    source = Column(String(128))
    urltype = Column(String(128))


class URLResponseTable(ORMBase):
    __tablename__ = "url_response_table"
    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    source = Column(String(128))
    sourceid = Column(String(40))
    responsecode = Column(Integer())
    responseheaders = Column(String(2048))
    responsetime = Column(String(128))
    tags = Column(String(256))


def create_schema(db_engine):
    ORMBase.metadata.create_all(db_engine)
    return db_engine