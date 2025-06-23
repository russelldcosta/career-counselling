from pydantic import BaseModel

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
