from fastapi import FastAPI
from utils import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/spent_time")
def read_item():
    return get_spent_time()

@app.get("/daily_app_usage")
def read_item():
    return get_daily_app_usage()
