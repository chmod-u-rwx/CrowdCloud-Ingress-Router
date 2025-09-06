from fastapi import FastAPI
from src.routes import route_parser

app = FastAPI()
app.include_router(route_parser.router)