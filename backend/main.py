from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL, echo=True)   # Create Async Engine
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)   # Session Factory
Base = declarative_base()   # Base Model



app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/homepage")
def get_homepage_data():
    return {
        "slogan": "Explore Your Future",
        "services": ["Career Test", "Skill Report", "Career Library"],
        "reviews": ["Amazing platform!", "Helped me choose my path!"],
        "contact_email": "support@careerguidance.com"
    }
