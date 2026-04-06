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

# /stocks/005930/history?day=60&market=kospi
@app.get("/stocks/{ticker}/{service}")
def get_stock_info(ticker:str, service:str, day:int, market:str) : 
    
    message = {}
    message['종목명'] = ticker
    message['서비스'] = service
    message['일자'] = day
    message['장구분'] = market
    
    # message = f"'종목명' : {ticker}, '서비스' : {service}, '일자' : {day}, '장구분' : {market}"
    # return {
    #     "종목명": ticker,
    #     "서비스": service,
    #     "일자": day,
    #     "장구분": market
    # }
    
    return  message

# uvicorn 03_advanced_app:app --reload --port 8003
