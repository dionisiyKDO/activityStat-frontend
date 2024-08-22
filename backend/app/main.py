from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import *

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/app_list")
def app_list():
    return JSONResponse(content=get_app_list())

@app.get("/spent_time")
def spent_time():
    return get_spent_time()

@app.get("/daily_app_usage/{app_name}")
def daily_app_usage(app_name: str):
    return get_daily_app_usage(app_name)
