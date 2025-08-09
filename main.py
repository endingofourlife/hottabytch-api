import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import v1_router
from src.config import lifespan

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix='/api', tags=['v1'])