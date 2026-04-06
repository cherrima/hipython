from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

class News(BaseModel) :
    title:str
    content:str
    views:int=0
    
    
@app.post("/news") 
def analyze_news(news:News) :
    return {"news":news.title}

# uvicorn 03_advanced_app:app --reload --port 8003
