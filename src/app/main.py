from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import main_router
from app.core.config import setup_logging

app = FastAPI()
app.include_router(main_router)

logger = setup_logging()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для теста
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
