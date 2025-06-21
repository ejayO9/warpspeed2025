from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import users_router
from database import engine

# Create tables
from app.models.base import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FinBuddy API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# Set all CORS enabled origins
# In a production environment, you should restrict this to your frontend's domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router, prefix="/api/v1/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "Welcome to FinBuddy"} 