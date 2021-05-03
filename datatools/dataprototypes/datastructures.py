from sqlalchemy import Table, Column, Integer, String, MetaData
meta = MetaData()

url_table = Table('urls', 
             meta, 
             Column('id', Integer, primary_key = True), 
             Column('value', String),
             Column('source', String)  
)


subdomain_table = Table('subdomains', 
             meta, 
             Column('id', Integer, primary_key = True), 
             Column('name', String), 
             Column('lastname', String), 
)

def create_schema(db_engine):
    meta.create_all(db_engine)
    return db_engine