from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base


ORMBase = declarative_base()
meta = MetaData()


class URLInputTable(ORMBase):
    __tablename__ = "url_table"
    id = Column(Integer, primary_key=True)
    value = Column(String(255))
    source = Column(String(255))




subdomain_table = Table('subdomains', 
             meta, 
             Column('id', Integer, primary_key = True), 
             Column('name', String), 
             Column('lastname', String), 
)

def create_schema(db_engine):
    ORMBase.metadata.create_all(db_engine)
    return db_engine