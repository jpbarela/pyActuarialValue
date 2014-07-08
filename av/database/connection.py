from pkg_resources import resource_filename

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

database_file = resource_filename("av","data/av.db" )

engine = create_engine('sqlite:///'+database_file, convert_unicode=True)

Session = sessionmaker(bind=engine)