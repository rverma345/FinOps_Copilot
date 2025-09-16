from src.api.schemas import KPIResponse,AskRequest,AskResponse
from fastapi import FastAPI, Query


app= FastAPI()

@app.get("/")
def read_root():
    return {'message':"hello,fastapi is running!"}