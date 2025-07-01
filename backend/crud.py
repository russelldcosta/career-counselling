# crud/career.py - Contains logic for - Creating a career page, Getting all career pages, Getting a page by slug
from sqlalchemy.orm import Session
from models import CareerPage
from schemas import CareerPageCreate

def create_career_page(db: Session, page: CareerPageCreate):
    db_page = CareerPage(**page.dict())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def get_all_pages(db: Session):
    return db.query(CareerPage).all()

def get_page_by_slug(db: Session, slug: str):
    return db.query(CareerPage).filter(CareerPage.slug == slug).first()
