from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from pydantic import BaseModel
from models import Base, Student

# Database config
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create FastAPI app
app = FastAPI()

# CORS middleware for frontend communication and authentication?
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample GET endpoint for homepage (optional)
@app.get("/homepage")
def get_homepage_data():
    return {
        "slogan": "Explore Your Future",
        "services": ["Career Test", "Skill Report", "Career Library"],
        "reviews": ["Amazing platform!", "Helped me choose my path!"],
        "contact_email": "support@careerguidance.com"
    }









# Create request body model
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    grade: str
    email: str
    country: str
    phone: str
    password: str

@app.post("/register")
def register_student(student: StudentCreate):   # ✅ Expect full JSON body
    session = SessionLocal()
    existing_student = session.query(Student).filter(Student.email == student.email).first()

    if existing_student:
        session.close()
        raise HTTPException(status_code=400, detail="Email already registered.")

    new_student = Student(
        first_name=student.first_name,
        last_name=student.last_name,
        grade=student.grade,
        email=student.email,
        country=student.country,
        phone=student.phone,
        password=student.password  # we will hash it later
    )

    session.add(new_student)
    session.commit()
    session.close()

    return {"message": "Student registered successfully!"}




@app.post("/login")
def login_student(email: str, password: str):
    session = SessionLocal()
    student = session.query(Student).filter(Student.email == email, Student.password == password).first()
    session.close()

    if student is None:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    
    return {"message": "Login successful", "first_name": student.first_name}
