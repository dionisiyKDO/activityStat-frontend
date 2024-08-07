from fastapi import FastAPI
from app.utils import *

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items")
def read_item():
    df_og = get_df()
    return total_spent_time(df_og)

