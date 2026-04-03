from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}

# 경로를 매개변수로, Handler
@app.get("/hello/{name}") 
def hello(name: str):  
    return {"message": f"Hello, {name}!"}

@app.get("/hello")
def hello_query(name: str):
    return {"message": f"Hello, {name}!"}

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


@app.get("/items/{item_id}") 
async def read_item(item_id : int) : 
    print(f"{item_id}를 받았습니다.")
    return {"item_id": item_id}



import uvicorn

if __name__ == "__main__":
    uvicorn.run("exam1:app", host="127.0.0.1", port=8000, reload=True)