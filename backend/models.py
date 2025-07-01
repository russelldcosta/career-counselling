# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

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







class CareerTest(Base):
    __tablename__ = "career_tests"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    number_of_questions = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("career_tests.id"))
    description = Column(String)
    tag = Column(String)

    test = relationship("CareerTest", back_populates="questions")








class CareerPage(Base):
    __tablename__ = "career_pages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, index=True)
    thumbnail_url = Column(String(500))
    slug = Column(String(200), unique=True, index=True)
    content = Column(Text)  # HTML from WYSIWYG
    riasec_tags = Column(String(20))  # Comma-separated e.g. "R,I"
    created_at = Column(DateTime(timezone=True), server_default=func.now())




