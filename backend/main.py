from fastapi import FastAPI, HTTPException, Query, APIRouter, Depends, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
import shutil, os
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from pydantic import BaseModel
from models import Base, Student, Admin, CareerTest, Question, datetime, CareerPage
from schemas import StudentSchema, CareerTestSchema, CareerTestCreateSchema, CareerTestUpdateSchema, Optional, CareerPageCreate, CareerPageOut
from crud import create_career_page, get_all_pages, get_page_by_slug
from typing import List
from uuid import uuid4





# Database config
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
# Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create FastAPI app
app = FastAPI()

# CORS middleware for frontend communication and authentication?
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # or ["*"] for all
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












# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @app.post("/admin/tests/create", response_model=CareerTestSchema)
# def create_career_test(test_data: CareerTestCreateSchema, db: Session = Depends(get_db)):
#     new_test = CareerTest(
#         name=test_data.name,
#         description=test_data.description,
#         number_of_questions=test_data.number_of_questions,
#         last_updated=datetime.utcnow()
#     )

#     for q in test_data.questions:
#         question = Question(description=q.description, tag=q.tag)
#         new_test.questions.append(question)

#     db.add(new_test)
#     db.commit()
#     db.refresh(new_test)
#     return CareerTestSchema.model_validate(new_test, from_attributes=True)



@app.post("/admin/tests/create", response_model=CareerTestSchema)
def create_career_test(test: CareerTestCreateSchema, db: Session = Depends(get_db)):
    new_test = CareerTest(
        name=test.name,
        description=test.description,
        number_of_questions=test.number_of_questions,
        last_updated=datetime.utcnow()
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # Save questions
    for q in test.questions:
        new_question = Question(
            test_id=new_test.id,
            description=q.description,
            tag=q.tag
        )
        db.add(new_question)

    db.commit()
    return CareerTestSchema.model_validate(new_test, from_attributes=True)





@app.get("/admin/tests", response_model=list[CareerTestSchema])
def get_all_tests(db: Session = Depends(get_db)):
    tests = db.query(CareerTest).all()
    return [CareerTestSchema.model_validate(t, from_attributes=True) for t in tests]





@app.get("/admin/tests/{test_id}", response_model=CareerTestSchema)
def get_test(test_id: int, db: Session = Depends(get_db)):
    test = db.query(CareerTest).filter(CareerTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return CareerTestSchema.model_validate(test, from_attributes=True) # return CareerTestSchema.model_validate(test)


@app.put("/admin/tests/{test_id}/update", response_model=CareerTestSchema)
def update_career_test(test_id: int, updated_data: CareerTestUpdateSchema, db: Session = Depends(get_db)):
    test = db.query(CareerTest).filter(CareerTest.id == test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Update test fields
    test.name = updated_data.name
    test.description = updated_data.description
    test.number_of_questions = updated_data.number_of_questions
    test.last_updated = datetime.utcnow()

    # Clear existing questions
    test.questions.clear()

    # Add new questions
    for q in updated_data.questions:
        question = Question(description=q.description, tag=q.tag)
        test.questions.append(question)

    db.commit()
    db.refresh(test)
    return CareerTestSchema.model_validate(test, from_attributes=True)



@app.post("/admin/tests/{test_id}/duplicate")
def duplicate_test(test_id: int, payload: CareerTestUpdateSchema, db: Session = Depends(get_db)):
    new_test = CareerTest(
        name=payload.name + " (Copy)",
        description=payload.description,
        number_of_questions=payload.number_of_questions,
        last_updated=datetime.utcnow()
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    for q in payload.questions:
        new_q = Question(description=q.description, tag=q.tag, test_id=new_test.id)
        db.add(new_q)

    db.commit()
    return {"message": "New test version created", "new_test_id": new_test.id }












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




UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.post("/career-pages/upload", response_model=CareerPageOut)
async def create_page(
    title: str = Form(...),
    slug: str = Form(...),
    content: str = Form(...),
    riasec_tags: Optional[str] = Form(""),
    parent_id: Optional[int] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    thumbnail_url = None
    if thumbnail:
        file_location = f"uploads/{thumbnail.filename}"
        with open(file_location, "wb") as f:
            f.write(await thumbnail.read())
        thumbnail_url = f"/{file_location}"

    # ✅ NO CareerPageCreate used here
    page = CareerPage(
        title=title,
        slug=slug,
        content=content,
        riasec_tags=riasec_tags,
        parent_id=parent_id,
        thumbnail_url=thumbnail_url
    )

    db.add(page)
    db.commit()
    db.refresh(page)
    return page






# List all career pages
@app.get("/career-pages", response_model=List[CareerPageOut])
def get_all_career_pages(db: Session = Depends(get_db)):
    return get_all_pages(db)


# Get a page by slug (for detail view)
@app.get("/career-pages/{slug}", response_model=CareerPageOut)
def get_page(slug: str, db: Session = Depends(get_db)):
    db_page = get_page_by_slug(db, slug)
    if not db_page:
        raise HTTPException(status_code=404, detail="Page not found.")
    return db_page

@app.put("/career-pages/{slug}/update")
def update_career_page(
    slug: str,
    title: str = Form(...),
    slug_new: Optional[str] = Form(None),
    riasec_tags: Optional[str] = Form(None),
    content: str = Form(...),
    parent_id: Optional[int] = Form(None),
    thumbnail: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    page = db.query(CareerPage).filter(CareerPage.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    page.title = title
    page.riasec_tags = riasec_tags
    page.content = content
    page.parent_id = parent_id

    if slug_new:
        page.slug = slug_new

    if thumbnail:
        filename = f"{uuid4().hex}_{thumbnail.filename}"
        file_location = f"static/uploads/{filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(thumbnail.file.read())
        page.thumbnail_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(page)
    return page



















if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
