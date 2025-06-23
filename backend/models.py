# models.py

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    grade = Column(String)
    email = Column(String, unique=True, index=True)
    country = Column(String)
    phone = Column(String)
    password = Column(String)  # hashed
    premium = Column(Boolean, default=False)
    career_test_count = Column(Integer, default=0)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    country = Column(String)
    phone = Column(String)
    password = Column(String)  # hashed

# create DB connection
engine = create_engine("sqlite:///test.db")
Base.metadata.create_all(bind=engine)
