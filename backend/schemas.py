from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StudentSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    grade: str
    email: str
    country: str
    phone: str
    premium: bool
    career_test_count: int

    class Config:
        orm_mode = True         #tells pydantic to read data from ORM objects which is my database











class QuestionSchema(BaseModel):
    id: Optional[int]
    description: str
    tag: str

    class Config:
        from_attributes = True

class CareerTestSchema(BaseModel):
    id: int
    name: str
    description: str
    number_of_questions: int
    questions: List[QuestionSchema]
    last_updated: datetime

    class Config:
        from_attributes = True

class QuestionCreateSchema(BaseModel):
    description: str
    tag: str

class CareerTestCreateSchema(BaseModel):
    name: str
    description: str
    number_of_questions: int
    questions: List[QuestionCreateSchema]

    class Config:
        from_attributes = True

class CareerTestUpdateSchema(BaseModel):
    name: str
    description: str
    number_of_questions: int
    questions: List[QuestionSchema]













class CareerPageBase(BaseModel):
    title: str
    slug: str
    content: str
    thumbnail_url: Optional[str] = None
    riasec_tags: Optional[str] = ""

class CareerPageCreate(CareerPageBase):
    pass

class CareerPageOut(CareerPageBase):
    id: int
    class Config:
        from_attributes = True