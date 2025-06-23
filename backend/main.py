from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from pydantic import BaseModel
from models import Base, Student, Admin
from fastapi import Query, APIRouter, Depends
from schemas import StudentSchema


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
    allow_origins=["http://localhost:3000"],  # replace * with your frontend port if needed
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







class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(credentials: LoginRequest):           #Use a Pydantic model to parse JSON POST request body from react
    email = credentials.email
    password = credentials.password

    session = SessionLocal()

    student = session.query(Student).filter(Student.email == email).first()
    if student and student.password == password:
        session.close()
        return {"role": "student", "message": "Student login successful"}

    admin = session.query(Admin).filter(Admin.email == email).first()
    if admin and admin.password == password:
        session.close()
        return {"role": "admin", "message": "Admin login successful"}

    session.close()
    raise HTTPException(status_code=401, detail="Invalid email or password")










#Reorder this over admin/id get request else it mistakes admin/students as admin/id
#SQLAlchemy returns ORM objects, not json serializable but FastAPI expects dict/list of primitives so we manually build a list of dict result
@app.get("/admin/students", response_model=list[StudentSchema])
def get_all_students(
    search: str = Query("", description="Search string"),
    sort_by: str = Query("id", enum=["id", "first_name", "last_name", "grade", "country", "email"]),
    order: str = Query("asc", enum=["asc", "desc"])
):
    session = SessionLocal()
    query = session.query(Student)

    if search:
        query = query.filter(Student.first_name.contains(search))

    sort_column = getattr(Student, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    students = query.all()
    session.close()
    return students   # FastAPI will automatically serialize SQLAlchemy models into Pydantic models because of orm_mode=True
                      # Instead of serializing here itself, i put that in the schemas.py















# Fetch admin data
@app.get("/admin/{admin_id}")
def get_admin_profile(admin_id: int):
    session = SessionLocal()
    admin = session.query(Admin).filter(Admin.id == admin_id).first()
    session.close()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return {
        "id": admin.id,
        "first_name": admin.first_name,
        "last_name": admin.last_name,
        "email": admin.email,
        "country": admin.country,
        "phone": admin.phone
    }

# Update admin profile (except email)
@app.put("/admin/{admin_id}")
def update_admin_profile(admin_id: int, data: dict):
    session = SessionLocal()
    admin = session.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        session.close()
        raise HTTPException(status_code=404, detail="Admin not found")

    # Only allow updates to fields other than email
    admin.first_name = data.get("first_name", admin.first_name)
    admin.last_name = data.get("last_name", admin.last_name)
    admin.country = data.get("country", admin.country)
    admin.phone = data.get("phone", admin.phone)

    session.commit()
    session.close()
    return {"message": "Admin profile updated successfully"}