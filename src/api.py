from fastapi import FastAPI
from src.controller.ons_router import router as ons_router
app = FastAPI()
app.include_router(ons_router)