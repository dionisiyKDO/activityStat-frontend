from fastapi import FastAPI
from utils import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items")
def read_item():
    return get_spent_time()

