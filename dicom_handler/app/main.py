from fastapi import FastAPI
from app.api import routes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(routes.router)
