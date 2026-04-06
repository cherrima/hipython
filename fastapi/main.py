from fastapi import FastAPI
# CORS를 위한 미들웨어를 추가합니다.
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 설정: 모든 출처, 모든 메소드, 모든 헤더를 허용합니다.
# 실제 서비스에서는 보안을 위해 출처를 명시하는 것이 좋습니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": get_item_name(item_id)}


def get_item_name(item_id: int) -> str : 
    
    match item_id:
        case 1:
            return "데스크탑"
        case 2:
            return "워크스테이션"
        case 3:
            return "중형서버"
        case 4:
            return "대형서버"
        case 5 :
            return "슈퍼컴퓨터"
        case _ :
            return "알수없슴"
        

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
        