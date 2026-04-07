from fastapi import FastAPI
# CORS를 위한 미들웨어를 추가합니다.
from fastapi.middleware.cors import CORSMiddleware
from routers.items import router as items_router
from routers.login import router as login_router
from routers.file_upload import router as sentiment_router

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

app.include_router(items_router)
app.include_router(login_router)
app.include_router(sentiment_router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Router Application!"}


# uvicorn main_router:app --reload --port 8001