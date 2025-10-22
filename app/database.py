import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_MAIN = os.getenv("POSTGRES_MASTER_URL")

engine_main = create_engine(DATABASE_URL_MAIN)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_main)
Base_main = declarative_base()

DATABASE_URL = os.getenv("POSTGRES_REPLICA_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
