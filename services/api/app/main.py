from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .api.v1.health import router as health_router
from .api.v1.reviews import router as reviews_router

app = FastAPI(title="tkfs-api")

origins = os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(reviews_router, prefix="/api/v1")
