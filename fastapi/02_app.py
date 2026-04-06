from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}

# @app.get("/hello")
# def just_hello():
#     return {"message": "Hello!!!"}

# 경로를 매개변수로, Handler
@app.get("/hello/{name}") 
def hello_path(name: str):  
    return {"message": f"Hello, {name}!"}

@app.get("/hello")
def hello_handler(
    name: Optional[str] = None, 
    moniker: Optional[str] = None
):
    # 1. moniker 파라미터가 들어온 경우
    if moniker:
        moniker = moniker.strip('"\'')
        return {"message": f"Hello and nice to meet you, {moniker}!"}
    
    # 2. name 파라미터가 들어온 경우
    if name:
        name = name.strip('"\'')
        return {"message": f"Hello, {name}!"}
    
    # 3. 둘 다 없거나 빈 값인 경우
    return {"message": "Hello!!!"}



# http://127.0.0.1:8000/hello?name=Miyoung
# @app.get("/hello")
# def hello_query(name: str):
#     if len(name) > 0 :
#         return {"message": f"Hello, {name}!"}
#     else :
#         return {"message": f"Hello!!!"}
    
# @app.get("/hello")
# def hello_moniker(moniker: str):
#     if len(moniker) > 0 :
#         return {"message": f"Hello and nice to meet you, {moniker}!"}
#     else :
#         return {"message": f"Hello and nice to meet you!!!"}

@app.get("/test1")
def root1():
    return {"name": "둘리"}

@app.get("/test2")
def root2():
    return ['둘리', "또치", "도우너"]

@app.get("/test3")
def root3():
    return "<h>안녕</h>"

@app.get("/test4")
def root4():
    return 2026

@app.post("/echo")
def echo(data: dict) :
    return {"dict" : data}

# #경로 매개변수, 핸들러
# @app.get("/items/{item_id}")
# def read_item(item_id: int):
#     item_id = item_id*2
  
#     print(f'{item_id}를 받았습니다')
  
#     return {"ID":item_id}


#경로 매개변수, 핸들러
#http:127.0.0.1;8000/items/37?discount=True
@app.get("/items/{item_id}")
def get_item(item_id: int, discount:bool=False):
    
    message = f"품목 {item_id}을(를) 할인{'받아' if discount else '없이'} 구매하였습니다."
  
    return {"Message":message}

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



import uvicorn

if __name__ == "__main__":
    uvicorn.run("exam1:app", host="127.0.0.1", port=8000, reload=True)