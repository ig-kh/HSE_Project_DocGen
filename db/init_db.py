# init db script. run by python app/db/init_db.py
from db.session import engine
from db.models import Base

Base.metadata.create_all(bind=engine)
