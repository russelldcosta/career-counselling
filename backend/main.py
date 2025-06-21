from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
